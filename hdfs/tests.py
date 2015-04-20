from django.test import TestCase
# limitations under the License.
#!/usr/bin/env python
import json
import os
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal

from utils.lib.django_test_util import make_logged_in_client
from utils.hadoop import pseudo_hdfs4


class Test(TestCase):
    # Create your tests here.
    def test_touch(self):
      cluster = pseudo_hdfs4.shared_cluster()
      cluster.fs.setuser('test')
      c = make_logged_in_client()
    
      try:
        success_path = 'touch_file'
        path_absolute = '/touch_file'
        path_fail = 'touch_fail/file'
        prefix = '/tmp/test-hdfs-touch/'
    
        cluster.fs.mkdir(prefix)
    
        resp = c.post('/hdfs/touch', dict(path=prefix, name=path_fail))
        assert_equal(500, resp.status_code)
        resp = c.post('/hdfs/touch', dict(path=prefix, name=path_absolute))
        assert_equal(500, resp.status_code)
        resp = c.post('/hdfs/touch', dict(path=prefix, name=success_path))
        assert_equal(200, resp.status_code)
    
        # Read the parent dir and make sure we created 'success_path' only.
        response = c.get('/hdfs/view' + prefix)
        file_listing = response.context['files']
        print 'result:'
        print file_listing
        assert_equal(3, len(file_listing))
        assert_equal(file_listing[2]['name'], success_path)
    
      finally:
        try:
          cluster.fs.rmtree(prefix)
        except:
          pass


@attr('requires_hadoop')
def test_upload_file():
  """Test file upload"""
  cluster = pseudo_hdfs4.shared_cluster()

  try:
    USER_NAME = 'test'
    HDFS_DEST_DIR = "/tmp/fb-upload-test"
    LOCAL_FILE = __file__
    HDFS_FILE = HDFS_DEST_DIR + '/' + os.path.basename(__file__)

    cluster.fs.setuser(USER_NAME)
    client = make_logged_in_client(USER_NAME)

    cluster.fs.do_as_superuser(cluster.fs.mkdir, HDFS_DEST_DIR)
    cluster.fs.do_as_superuser(cluster.fs.chown, HDFS_DEST_DIR, USER_NAME, USER_NAME)
    cluster.fs.do_as_superuser(cluster.fs.chmod, HDFS_DEST_DIR, 0700)

    stats = cluster.fs.stats(HDFS_DEST_DIR)
    assert_equal(stats['user'], USER_NAME)
    assert_equal(stats['group'], USER_NAME)

    # Just upload the current python file
    resp = client.post('/project/webform/worker/fb/upload/file?dest=%s' % HDFS_DEST_DIR, # GET param avoids infinite looping
                       dict(dest=HDFS_DEST_DIR, hdfs_file=file(LOCAL_FILE)))
    result = resp.content
    response = json.loads(result)

    assert_equal(0, response['status'], response)
    stats = cluster.fs.stats(HDFS_FILE)
    assert_equal(stats['user'], USER_NAME)
    assert_equal(stats['group'], USER_NAME)

    f = cluster.fs.open(HDFS_FILE)
    actual = f.read()
    expected = file(LOCAL_FILE).read()
    assert_equal(actual, expected)

    # Upload again and so fails because file already exits
    resp = client.post('/project/webform/worker/fb/upload/file?dest=%s' % HDFS_DEST_DIR,
                       dict(dest=HDFS_DEST_DIR, hdfs_file=file(LOCAL_FILE)))
    response = json.loads(resp.content)
    assert_equal(-1, response['status'], response)
    assert_true('already exists' in response['data'], response)

  finally:
    try:
      cluster.fs.remove(HDFS_DEST_DIR)
    except Exception, ex:
      pass