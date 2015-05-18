# coding=utf-8
import errno
import logging
import time

from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers, StopUpload
from django.utils.translation import ugettext as _

import utils.hadoop.cluster

from utils.hadoop.conf import UPLOAD_CHUNK_SIZE
from utils.hadoop.fs.exceptions import WebHdfsException

LOG = logging.getLogger(__name__)


UPLOAD_SUBDIR = 'hue-uploads'


class HDFSerror(Exception):
  pass


class HDFStemporaryUploadedFile(object):
  """
  暂存在HDFS的上传文件
  """
  def __init__(self, request, name, destination):
    self.name = name #文件名
    self.size = None #文件大小
    self._do_cleanup = False #是否需要清理
    try:
      #中间间中设置的fs
      self._fs = request.fs
    except AttributeError:
      #从集群中获得fs实例
      self._fs = utils.hadoop.cluster.get_hdfs()

    #如果没有hdfs,则报错
    if not self._fs:
      raise HDFSerror("No HDFS found")

    #设置fs操作用户为超级用户
    self._fs.setuser(self._fs.superuser)
    #设置临时文件的路径
    self._path = self._fs.mkswap(name, suffix='tmp', basedir=destination)
    #若文件存在，则替换
    if self._fs.exists(self._path):
      self._fs._delete(self._path)
    self._file = self._fs.open(self._path, 'w')
    #设置为需要清理
    self._do_cleanup = True

  def __del__(self):
    if self._do_cleanup:
      LOG.error("Upload file is not cleaned up: %s" % (self._path,))

  def get_temp_path(self):
    return self._path

  def finish_upload(self, size):
    try:
      self.size = size
      self.close()
    except Exception, ex:
      LOG.exception('Error uploading file to %s' % (self._path,))
      raise

  def remove(self):
    try:
      # 删除文件
      self._fs.remove(self._path, True)
      # 设置清理完毕
      self._do_cleanup = False
    except IOError, ex:
      if ex.errno != errno.ENOENT:
        LOG.exception('Failed to remove temporary upload file "%s". '
                      'Please cleanup manually: %s' % (self._path, ex))

  def write(self, data):
    self._file.write(data)

  def flush(self):
    self._file.flush()

  def close(self):
    self._file.close()


class HDFSfileUploadHandler(FileUploadHandler):

  def __init__(self, request):
    FileUploadHandler.__init__(self, request)
    self._file = None #文件
    self._starttime = 0 #上传时间
    self._activated = False #是否开始
    self._destination = request.GET.get('dest', None) # 目标位置
    self.request = request
    #设置上传块大小
    FileUploadHandler.chunk_size = UPLOAD_CHUNK_SIZE.get()

  def new_file(self, field_name, file_name, *args, **kwargs):
    # 检测以"FIlE"打头的前缀
    if field_name.upper().startswith('FILE'):
      try:
        # 初始化文件
        self._file = HDFStemporaryUploadedFile(self.request, file_name, self._destination)
        LOG.debug('Upload attempt to %s' % (self._file.get_temp_path(),))
        self._activated = True
        self._starttime = time.time()
      except Exception, ex:
        LOG.error("Not using HDFS upload handler: %s" % (ex,))
        self.request.META['upload_failed'] = ex
      #停止上传
      raise StopFutureHandlers()

  def receive_data_chunk(self, raw_data, start):
    if not self._activated:
      if self.request.META.get('PATH_INFO').startswith('/hdfs') and self.request.META.get('PATH_INFO') != '/hdfs/upload/archive':
        raise StopUpload()
      return raw_data

    try:
      # 写文件
      self._file.write(raw_data)
      self._file.flush()
      return None
    except IOError:
      LOG.exception('Error storing upload data in temporary file "%s"' %
                    (self._file.get_temp_path(),))
      raise StopUpload()

  def file_complete(self, file_size):
    if not self._activated:
      return None

    try:
      # 结束上传
      self._file.finish_upload(file_size)
    except IOError:
      LOG.exception('Error closing uploaded temporary file "%s"' %
                    (self._file.get_temp_path(),))
      raise
    # 总耗时
    elapsed = time.time() - self._starttime
    LOG.debug('Uploaded %s bytes to HDFS in %s seconds' % (file_size, elapsed))
    return self._file