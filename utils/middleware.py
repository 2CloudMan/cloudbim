'''
Created on Apr 3, 2015

@author: linmiancheng
'''
from utils.hadoop import cluster
class ClusterMiddleware(object):
  """
  Manages setting request.fs and request.jt
  """
  def process_view(self, request, view_func, view_args, view_kwargs):
    """
    Sets request.fs and request.jt on every request to point to the
    configured filesystem.
    """
    request.fs_ref = request.REQUEST.get('fs', view_kwargs.get('fs', 'default'))
    if "fs" in view_kwargs:
      del view_kwargs["fs"]

    try:
      request.fs = cluster.get_hdfs(request.fs_ref)
    except KeyError:
      raise KeyError(_('Cannot find HDFS called "%(fs_ref)s".') % {'fs_ref': request.fs_ref})

    if request.user.is_authenticated():
      if request.fs is not None:
        request.fs.setuser(request.user.username)

      request.jt = cluster.get_default_mrcluster() # Deprecated, only there for MR1
      if request.jt is not None:
        request.jt.setuser(request.user.username)
    else:
      request.jt = None