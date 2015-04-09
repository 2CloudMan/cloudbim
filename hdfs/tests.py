from django.test import TestCase
# limitations under the License.
#!/usr/bin/env python

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
