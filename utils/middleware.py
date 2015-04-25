'''
Created on Apr 3, 2015

@author: linmiancheng
'''
import logging

from utils.lib.django_util import render, render_json
from utils.hadoop import cluster
from utils.lib.exceptions_renderable import PopupException
from utils.lib.exceptions import StructuredException

from utils.lib import  i18n
from admin.models import get_profile
from django.utils.translation import ugettext, ugettext_lazy as _
from django.conf import settings

LOG = logging.getLogger(__name__)


MIDDLEWARE_HEADER = "X-Cloudbim-Middleware-Response"
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


class GroupMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated() and 'proj_slug' in view_kwargs\
                and 'role_slug' in view_kwargs:

            try:
                request.group = get_profile(request.user).get_group(view_kwargs['proj_slug'], view_kwargs['role_slug'])
                if not request.group:
                    raise Exception('you are not a %s of project %s' % (view_kwargs['proj_slug'],
                                                                        view_kwargs['role_slug']))
            except Exception as e:
                raise PopupException('%s' % e)
        else:
            request.group = None
        
class ExceptionMiddleware(object):
    """
    If exceptions know how to render themselves, use that.
    """
    def process_exception(self, request, exception):
        import traceback
        tb = traceback.format_exc()
        logging.info("Processing exception: %s: %s" % (i18n.smart_unicode(exception),
                                                       i18n.smart_unicode(tb)))
        
        if isinstance(exception, PopupException):
            return exception.response(request)
        
        if isinstance(exception, StructuredException):
            if request.ajax:
                response = render_json(exception.response_data)
                response[MIDDLEWARE_HEADER] = 'EXCEPTION'
                response.status_code = getattr(exception, 'error_code', 500)
                return response
            else:
                response = render("error.mako", request,
                              dict(error=exception.response_data.get("message")))
                response.status_code = getattr(exception, 'error_code', 500)
                return response
        
        return None


class AjaxMiddleware(object):
  """
  Middleware that augments request to set request.ajax
  for either is_ajax() (looks at HTTP headers) or ?format=json
  GET parameters.
  """
  def process_request(self, request):
    request.ajax = request.is_ajax() or request.REQUEST.get("format", "") == "json"
    return None
