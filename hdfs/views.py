# coding=utf-8
import os
import posixpath
import stat
import json
import logging
from datetime import datetime
from django.utils.translation import ugettext as _
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods

from utils.lib.django_util import  format_preserving_redirect
from utils.lib.django_util import render
from utils.lib.exceptions_renderable import PopupException
from utils.hadoop.fs.hadoopfs import Hdfs
from utils.hadoop.fs.exceptions import WebHdfsException
from utils.lib import paginator
from django.http import HttpResponse
from hdfs.forms import UploadFileForm, MkDirForm, RmTreeFormSet
from admin.models import get_project_dir, get_profile
from admin.views import ensure_project_directory

Log = logging.getLogger(__name__)
def view(request, proj_slug, role_slug, path):



    return listdir_paged(request, proj_slug, role_slug, path)


def listdir_paged(request, proj_slug, role_slug, path):
    """
    分页显示目录下的文件
    data = {
        'user' : user,
        'curr_proj': proj_slug,
        'curr_role': role_slug,
        'path': '',
        'raw_path': '',
        'breadcrumbs': breadcrumbs,
        'files': files
        'pagenum': pagenum,
        'pagesize': pagesize
    }

    ps：
    1. breadcrumb 主要用于路径导航, breadcrumb - {'url': '', label:''}
    例如path = /mydir/myjobs/   （必须为目录） 则分解为两个breadcrumb 为
    {'url' : '/mydir/', 'label': 'mydir'} { 'url': '/mydir/myjobs/', 'label': 'myjobs'}
    2. file
   {
        'name': 'mywork',
        'path': '/mydir/mywork',
        'raw_path": '/project_slug/role_slug/mydir/mywork'
        'permission': '???',
        'human_size': '12kb',
        'project': 'proj_slug',
        'role':  'role_slug'
        'ctime': date,
        'atime': data,
        'isdir': false
    }
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/auth/login')
    
    # 判断给定的路径是否是在项目所在的目录下
    project_home = get_project_dir(request.group.groupprofile.project)
    if not path.startswith(project_home):
        raise PopupException('The given path not in the project path')

    # 检查项目目录是否存在，不存在就创建
    if not request.fs.isdir(project_home):
        ensure_project_directory(request.fs, request.group.groupprofile.project.slug)
    
    # 判断给定路径是否是一个目录
    if not request.fs.isdir(path):
        Log.warn('user %s try to open a dir user the given path %s but it is not a directory!' %
                (request.user.username, path)) 
        raise Exception("Not a directory: %s" % (path,))
#         raise PopupException("Not a directory: %s" % (path,))
    
    # 用户是否有查看目录的权限
    
    if get_profile(request.user).has_file_permission(request.group, path, 'r')\
            or request.user.is_superuser:
        pagenum = int(request.GET.get('pagenum', 1))
        pagesize = int(request.GET.get('pagesize', 30))
        
        breadcrumbs = parse_breadcrumbs(path)
        dir_list = request.fs.do_as_user(request.user.username, request.fs.listdir_stats, path)
    # Filter
    # 排序
    
    # 分页
        page = paginator.Paginator(dir_list, pagesize).page(pagenum)
        shown_stats = page.object_list
    # 添加父目录
        # Include parent dir always as second option, unless at filesystem root.
        if Hdfs.normpath(path) != posixpath.sep:
            parent_path = request.fs.join(path, "..")
            parent_stat = request.fs.stats(parent_path)
            # The 'path' field would be absolute, but we want its basename to be
            # actually '..' for display purposes. Encode it since _massage_stats expects byte strings.
            parent_stat['path'] = parent_path
            parent_stat['name'] = ".."
            shown_stats.insert(0, parent_stat)
    
        # Include same dir always as first option to see stats of the current folder
        current_stat = request.fs.stats(path)
        # The 'path' field would be absolute, but we want its basename to be
        # actually '.' for display purposes. Encode it since _massage_stats expects byte strings.
        current_stat['path'] = path
        current_stat['name'] = "."
        shown_stats.insert(1, current_stat)
    
        files = [ _massage_stats(request, s) for s in shown_stats ]


        data = \
        {
            'user' : request.user,
            'curr_proj': proj_slug,
            'curr_role': role_slug,
            'path': '',
            'raw_path': path,
            'breadcrumbs': breadcrumbs,
            'files': files,
            'pagenum': pagenum,
            'pagesize': pagesize
        }
        Log.info("User %s open directory %s" % (request.user.username, path))
    else:
        # 这里应该添加权限限制提醒
        Log.warn("Permission deny: user %s try to open directory %s" %
                 (request.user.username, path))
        data = {'error': 'Permission deny'}
    return render('listdir.mako', request, data)


def _massage_stats(request, stats):
    """
    Massage a stats record as returned by the filesystem implementation
    into the format that the views would like it in.
    """
    path = stats['path']
    normalized = Hdfs.normpath(path)
    proj_slug = ''
    role_slug = ''
#     group = stats['group']
#     group_info =  group.split(':')
#     if group_info != 2:
#         return None
#     proj_slug, role_slug = group_info
#     
        
    return {
        'name': stats['name'],
        'path': '',
        'raw_path': normalized,
        'permission': '???',
        'human_size': '12kb',
        'project': proj_slug,
        'role':  role_slug,
        'ctime': datetime.fromtimestamp(stats['mtime']).strftime('%B %d, %Y %I:%M %p'),
        'atime': datetime.fromtimestamp(stats['atime']).strftime('%B %d, %Y %I:%M %p'),
        'isdir': stat.S_ISDIR(stats['mode']),
    }
    
    
def parse_breadcrumbs(path):
    breadcrumbs_parts = Hdfs.normpath(path).split('/')
    i = 1
    breadcrumbs = [{'url': '', 'label': '/'}]
    while (i < len(breadcrumbs_parts)):
        breadcrumb_url = breadcrumbs[i - 1]['url'] + '/' + breadcrumbs_parts[i]
        if breadcrumb_url != '/':
            breadcrumbs.append({'url': breadcrumb_url, 'label': breadcrumbs_parts[i]})
        i = i + 1
    return breadcrumbs

def upload_file(request, proj_slug, role_slug) :

    """
    :param request:
    :param proj_slug:
    :param role_slug:
    :return  json
            成功： {code: ０}
            失败： {code: 1, errMsg: '例如：文件以存在'}

    post 方法
    参数为dest : 目标目录路径（才角色目录为根目录）
         file ：
    """

    response = {'status': -1, 'data': ''}
    
    # 登录验证
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/auth/login')
    
    if request.method == 'POST':
        try:
            resp = _upload_file(request)
            response.update(resp)
        except Exception, ex:
            response['data'] = str(ex)
            Log.error('file upload fail')  # 需要更详细的描述
            hdfs_file = request.FILES.get('hdfs_file')
            if hdfs_file:
                hdfs_file.remove()
    else:
        response['data'] = _('A POST request is required.')

    return HttpResponse(json.dumps(response), content_type="text/plain")


def _upload_file(request):
    """
    Handles file uploaded by HDFSfileUploadHandler.

    The uploaded file is stored in HDFS at its destination with a .tmp suffix.
    We just need to rename it to the destination path.
    """
    
    form = UploadFileForm(request.POST, request.FILES)
    response = {'status': -1, 'data': ''}

    if request.META.get('upload_failed'):
      raise PopupException(request.META.get('upload_failed'))

    if form.is_valid():
        uploaded_file = request.FILES['hdfs_file']
        dest = form.cleaned_data['dest']

        if request.fs.isdir(dest) and posixpath.sep in uploaded_file.name:
            raise PopupException(_('Sorry, no "%(sep)s" in the filename %(name)s.' %
                                   {'sep': posixpath.sep, 'name': uploaded_file.name}))
    
        # 判断用户是否有权限上传文件
        if not request.user.is_superuser and \
                not get_profile(request.user).has_file_permission(request.group, dest, 'w'):
            raise PopupException(_('Permission deny: user %(user) try upload file %(name)s to destination %(dest).' 
                                   % {'user': request.user.username, 'name': uploaded_file.name, 'dest': dest}))

        dest = request.fs.join(dest, uploaded_file.name)
        tmp_file = uploaded_file.get_temp_path()
#         username = request.user.username

        try:
            # Remove tmp suffix of the file
#             request.fs.do_as_user(username, request.fs.rename, tmp_file, dest)
            request.fs.do_as_superuser(request.fs.rename, tmp_file, dest)
            response['status'] = 0
            
            # 为文件创建权限
            
        except IOError, ex:
            already_exists = False
            try:
                already_exists = request.fs.exists(dest)
            except Exception:
              pass
            if already_exists:
                msg = _('Destination %(name)s already exists.')  % {'name': dest}
            else:
                msg = _('Copy to %(name)s failed: %(error)s') % {'name': dest, 'error': ex}
            raise PopupException(msg)

        response.update({
          'path': dest,
          'result': _massage_stats(request, request.fs.stats(dest)),
          'next': request.GET.get("next")
        })

        return response
    else:
        raise PopupException(_("Error in upload form: %s") % (form.errors,))

def mkdir(request):
    def smart_mkdir(path, name):
        # Make sure only one directory is specified at a time.
        # No absolute directory specification allowed.
        if posixpath.sep in name or "#" in name:
            raise PopupException(_("Could not name folder \"%s\": Slashes or hashes are not allowed in filenames." % name))
        request.fs.mkdir(os.path.join(path, name))

    return generic_op(MkDirForm, request, smart_mkdir, ["path", "name"], "path")


def default_data_extractor(request):
    return {'data': request.POST.copy()}


def default_arg_extractor(request, form, parameter_names):
    return [form.cleaned_data[p] for p in parameter_names]


def default_initial_value_extractor(request, parameter_names):
    initial_values = {}
    for p in parameter_names:
        val = request.GET.get(p)
        if val:
            initial_values[p] = val
    return initial_values


def generic_op(form_class, request, op, parameter_names, piggyback=None, template="fileop.mako", data_extractor=default_data_extractor, arg_extractor=default_arg_extractor, initial_value_extractor=default_initial_value_extractor, extra_params=None):
    """
    Generic implementation for several operations.

    @param form_class form to instantiate
    @param request incoming request, used for parameters
    @param op callable with the filesystem operation
    @param parameter_names list of form parameters that are extracted and then passed to op
    @param piggyback list of form parameters whose file stats to look up after the operation
    @param data_extractor function that extracts POST data to be used by op
    @param arg_extractor function that extracts args from a given form or formset
    @param initial_value_extractor function that extracts the initial values of a form or formset
    @param extra_params dictionary of extra parameters to send to the template for rendering
    """
    # Use next for non-ajax requests, when available.
    next = request.GET.get("next", request.POST.get("next", None))

    ret = dict({
        'next': next
    })

    if extra_params is not None:
        ret['extra_params'] = extra_params

    for p in parameter_names:
        val = request.REQUEST.get(p)
        if val:
            ret[p] = val

    if request.method == 'POST':
        form = form_class(**data_extractor(request))
        ret['form'] = form
        if form.is_valid():
            args = arg_extractor(request, form, parameter_names)
            try:
                op(*args)
            except (IOError, WebHdfsException), e:
                msg = _("Cannot perform operation.")
                if request.user.is_superuser and not request.user == request.fs.superuser:
                    msg += _(' Note: you are a Hue admin but not a HDFS superuser (which is "%(superuser)s").') \
                           % {'superuser': request.fs.superuser}
                raise PopupException(msg, detail=e)
            if next:
                logging.debug("Next: %s" % next)
                # Doesn't need to be quoted: quoting is done by HttpResponseRedirect.
                return format_preserving_redirect(request, next)
            ret["success"] = True
            try:
                if piggyback:
                    piggy_path = form.cleaned_data[piggyback]
                    ret["result"] = _massage_stats(request, request.fs.stats(piggy_path))
            except Exception, e:
                # Hard to report these more naturally here.  These happen either
                # because of a bug in the piggy-back code or because of a
                # race condition.
                Log.exception("Exception while processing piggyback data")
                ret["result_error"] = True

            ret['user'] = request.user
            return render(template, request, ret)
    else:
        # Initial parameters may be specified with get with the default extractor
        initial_values = initial_value_extractor(request, parameter_names)
        formset = form_class(initial=initial_values)
        ret['form'] = formset
    return render(template, request, ret)


# @require_http_methods(["POST"])
# def rmtree(request):
#     """
#     delete a tree recursively
#     if skip_trash is true move  file or directory to trash.
#     Will create a timestamped directory underneath /user/<username>/.Trash.
#     """
#     recurring = []
#     params = ["path"]
#     def bulk_rmtree(*args, **kwargs):
#         for arg in args:
#             request.fs.do_as_user(request.user, request.fs.rmtree, arg['path'], 'skip_trash' in request.GET)
#     
#     data = {
#             # return something
#     }
#     return HttpResponse(data)
