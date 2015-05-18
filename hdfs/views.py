# coding=utf-8
import os
import posixpath
import stat
import json
import logging
import mimetypes
from datetime import datetime
from django.utils.translation import ugettext as _
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from django.http import Http404, HttpResponseNotModified
from django.utils.http import http_date
from django.utils.html import escape
from django.views.static import was_modified_since

from utils.lib.django_util import  format_preserving_redirect, JsonResponse
from utils.lib.django_util import render
from utils.lib.exceptions_renderable import PopupException
from utils.hadoop.fs.hadoopfs import Hdfs
from utils.hadoop.fs.exceptions import WebHdfsException
from utils.lib import paginator
from django.http import HttpResponse
from hdfs.forms import UploadFileForm, MkDirForm, RmTreeFormSet
from admin.models import get_project_dir, get_profile, ensure_new_fileinfo,\
    FileInfo, get_user_proj_roles_info, clear_file_info
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
    project_home, hadoop_path = get_hadoop_path(request, path)
    # 判断给定路径是否是一个目录
    if not request.fs.isdir(hadoop_path):
        Log.warn('user %s try to open a dir user the given path %s but it is not a directory!' %
                (request.user.username, hadoop_path)) 
        raise PopupException("Not a directory: %s" % (hadoop_path,))

    # 用户是否有查看目录的权限
    if get_profile(request.user).has_file_permission(request.group, hadoop_path, 'r'):
        # Filter
        # 排序
    
        dir_list = request.fs.do_as_superuser(request.fs.listdir_stats, hadoop_path)
        breadcrumbs = parse_breadcrumbs(path)
 
        # 分页
        pagenum = int(request.GET.get('pagenum', 1))
        pagesize = int(request.GET.get('pagesize', 30))
        page = paginator.Paginator(dir_list, pagesize).page(pagenum)

        shown_stats = page.object_list
        files = []

        for s in shown_stats:
            msg = _massage_stats(request, s, project_home)
            if msg:
                files.append(msg)

        page = _massage_page(page)
        proj_info, roles_info = get_user_proj_roles_info(request.user, request.group.groupprofile.project)
        data = \
        {
            'curr_proj': proj_slug,
            'curr_role': role_slug,
            'project': proj_info,
            'roles': roles_info,
            'path': path,
            'raw_path': hadoop_path,
            'breadcrumbs': breadcrumbs,
            'files': files,
            'page' : page,
            'pagenum': pagenum,
            'pagesize': pagesize
        }
        Log.info("User %s open directory %s" % (request.user.username, path))
    else:
        # 这里应该添加权限限制提醒
        Log.warn("Permission deny: user %s try to open directory %s" %
                 (request.user.username, path))
        raise PopupException('Permission deny!')

    # 返回格式控制
    format = request.GET.get('format', None)
    if format == 'json':
        return JsonResponse(data)

    data['user'] = request.user
    return render('listdir.mako', request, data)


def _massage_stats(request, stats, cur_path):
    """
    Massage a stats record as returned by the filesystem implementation
    into the format that the views would like it in.
    """
    relpath = '/'
    path = stats['path']
    normalized = Hdfs.normpath(path)

    if path.startswith(cur_path):
        relpath = '/' + posixpath.relpath(path, cur_path)
        Log.error("Get message stats error: the given current" + 
                        "path is not the parent %s of path%s - stats: %s" % (cur_path, path, stats))

    proj_slug = ''
    role_slug = ''
    owner = 'system'
    try:
        file = FileInfo.objects.get(path=path)
        owner = file.owner.username
    except FileInfo.DoesNotExist:
        Log.warn("Can't find file info of File %s" % path)
        return None

    return {
        'name': stats['name'],
        'path': relpath,
        'owner': owner,
        'raw_path': normalized,
        'permission': '???',
        'human_size': filesizeformat(stats['size']),
        'project': proj_slug,
        'role':  role_slug,
        'ctime': datetime.fromtimestamp(stats['mtime']).strftime('%Y-%m-%d %H:%M:%S'),
        'atime': datetime.fromtimestamp(stats['atime']).strftime('%Y-%m-%d %H:%M:%S'),
        'isdir': stat.S_ISDIR(stats['mode']),
    }

def _massage_page(page):
    return {
        'number': page.number,
        'num_pages': page.num_pages(),
        'previous_page_number': page.previous_page_number(),
        'next_page_number': page.next_page_number(),
        'start_index': page.start_index(),
        'end_index': page.end_index(),
        'total_count': page.total_count()
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

    next = request.GET.get("next", request.POST.get("next", None))


    response = {'status': -1, 'data': ''}
    
    # 登录验证
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/auth/login')
    
    if request.method == 'POST':
        try:
            resp = _upload_file(request)
            response.update(resp)
            if next:
                return HttpResponseRedirect(next)
        except Exception, ex:
            response['data'] = str(ex)
            Log.error('file upload fail', exc_info=True)  # 需要更详细的描述
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
        uploaded_file = request.FILES['file']
        dest = form.cleaned_data['dest']

        # 获取路径
        project_home, dest = get_hadoop_path(request, dest)

        if request.fs.isdir(dest) and posixpath.sep in uploaded_file.name:
            raise PopupException(_('Sorry, no "%(sep)s" in the filename %(name)s.' %
                                   {'sep': posixpath.sep, 'name': uploaded_file.name}))

        # 判断用户是否有权限上传文件
        if not get_profile(request.user).has_file_permission(request.group, dest, 'w'):
            raise PopupException(_('Permission deny: user %(user) try upload file %(name)s to destination %(dest).' 
                                   % {'user': request.user.username, 'name': uploaded_file.name, 'dest': dest}))

        dest = request.fs.join(dest, uploaded_file.name)
        tmp_file = uploaded_file.get_temp_path()

        try:
            # Remove tmp suffix of the file
#             request.fs.do_as_user(username, request.fs.rename, tmp_file, dest)
            request.fs.do_as_superuser(request.fs.rename, tmp_file, dest)
            response['status'] = 0

            # 为文件创建权限
            ensure_new_fileinfo(dest, request)

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
          'result': _massage_stats(request, request.fs.stats(dest), project_home),
          'next': request.GET.get("next")
        })

        return response
    else:
        raise PopupException(_("Error in upload form: %s") % (form.errors,))

def mkdir(request, proj_slug, role_slug):

    next = request.GET.get("next", request.POST.get("next", None))

    if request.method == 'POST':
        form = MkDirForm(request.POST)
        if form.is_valid():
            path = form.cleaned_data['dest']
            name = form.cleaned_data['dir_name']
            
            proj_home, hadoop_path = get_hadoop_path(request, path)

            if posixpath.sep in name or '#' in name:
                raise PopupException(_("Could not name folder \"%s\": " + 
                                       "Slashes or hashes are not allowed in filenames." % name))

            # 权限验证
            if not get_profile(request.user).has_file_permission(request.group, hadoop_path, 'w'):
                raise PopupException(_('Permission deny: user %(user)s try mkdir  %(name)s to destination %(dest)s.' 
                                       % {'user': request.user.username, 'name': name, 'dest': path}))

            dest = os.path.join(hadoop_path, name)
            try:
                request.fs.do_as_superuser(request.fs.mkdir, dest)

                # 为文件创建权限
                ensure_new_fileinfo(dest, request)
            except Exception as e:
                raise PopupException("Mkdir failed!: user %s try to mkdir in path %s" 
                                     % (request.user.username, dest))
                Log.error("Make dirrectory failed! ", exc_info=e)
            if next:
                logging.debug("Next: %s" % next)
                # Doesn't need to be quoted: quoting is done by HttpResponseRedirect.
                return format_preserving_redirect(request, next)

            return JsonResponse(dict(success=True, code=200))
        else:
            return JsonResponse(dict(success=False, error=form.errors, code=403))
    else:
        result = {"success": False, "error": "request a post method", 'code': 403}
        return JsonResponse(result)


def default_arg_extractor(request, form, parameter_names):
    return [form.cleaned_data[p] for p in parameter_names]


def default_data_extractor(request):
    return {'data': request.POST.copy()}


def default_initial_value_extractor(request, parameter_names):
    initial_values = {}
    for p in parameter_names:
        val = request.GET.get(p)
        if val:
            initial_values[p] = val
    return initial_values


def generic_op(form_class, request, op, parameter_names, piggyback=None,
               template="fileop.mako", data_extractor=default_data_extractor, arg_extractor=default_arg_extractor, initial_value_extractor=default_initial_value_extractor, extra_params=None):
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


def formset_arg_extractor(request, formset, parameter_names):
    data = []
    for form in formset.forms:
        data_dict = {}
        for p in parameter_names:
            data_dict[p] = form.cleaned_data[p]
        data.append(data_dict)
    return data


def formset_data_extractor(recurring=[], submitted=[]):
    """
    Builds a list of data that formsets should use by extending some fields to every object,
    whilst others are assumed to be received in order.
    Formsets should receive data that looks like this: [{'param1': <something>,...}, ...].
    The formsets should then handle construction on their own.
    """
    def _data_extractor(request):
        if not submitted:
            return []
        # Build data with list of in order parameters receive in POST data
        # Size can be inferred from largest list returned in POST data
        data = []
        for param in submitted:
            i = 0
            for val in request.POST.getlist(param):
                if len(data) == i:
                    data.append({})
                data[i][param] = val
                i += 1
        # Extend every data object with recurring params
        for kwargs in data:
            for recurrent in recurring:
                kwargs[recurrent] = request.POST.get(recurrent)
        initial = list(data)
        return {'initial': initial, 'data': data}

    return _data_extractor


@require_http_methods(["POST"])
def rmtree(request, proj_slug, role_slug):
    """
    delete a tree recursively
    if skip_trash is true move  file or directory to trash.
    Will create a timestamped directory underneath /user/<username>/.Trash.
    """
    recurring = []
    params = ["path"]

    def bulk_rmtree(*args, **kwargs):
        for arg in args:
        # 验证用户权限
            # 获取文件所在目录的权限
            dirname = posixpath.dirname(arg['path'])
            if not get_profile(request.user).has_file_permission(request.group, dirname, 'w'):
                # do more
                raise PopupException('Permission deny!!')
            # 如果用户是超级用户或者拥有写文件所在目录的写权限即可删除文件
            request.fs.do_as_superuser(request.fs.rmtree, arg['path'], 'skip_trash' in request.GET)
            # 暂时不能地柜删除文件，所以这里清理信息无需考虑递归清理
            clear_file_info(request, arg['path'])

    return generic_op(RmTreeFormSet, request, bulk_rmtree, ["path"], None,
                      data_extractor=formset_data_extractor(recurring, params),
                      arg_extractor=formset_arg_extractor,
                      initial_value_extractor=default_initial_value_extractor)


def _file_reader(fh):
    """Generator that reads a file, chunk-by-chunk."""
    while True:
        chunk = fh.read(settings.DOWNLOAD_CHUNK_SIZE)
        if chunk == '':
            fh.close()
            break
        yield chunk


def download(request, proj_slug, role_slug, path):
    """
    Downloads a file.

    This is inspired by django.views.static.serve.
    ?disposition={attachment, inline}
    """
    path = Hdfs.normpath(path)
    proj_home, hadoop_path = get_hadoop_path(request, path)
    file = FileInfo.objects.filter(path=hadoop_path).first()

    if not request.fs.exists(hadoop_path) or not file:
        raise Http404(_("File not found: %(path)s.") % {'path': escape(hadoop_path)})
    if not request.fs.isfile(hadoop_path):
        raise PopupException(_("'%(path)s' is not a file.") % {'path': hadoop_path})

    # //权限判断
    profile = get_profile(request.user)
    if not profile.has_file_permission(request.group, hadoop_path, 'w'): raise PopupException(_('Permission deny: user %(user) try download  file %(name)s.' 
                               % {'user': request.user.username, 'name': hadoop_path}))
 
    # 添加用户日志
    profile.userlog_download(file, 'file download')
    content_type = mimetypes.guess_type(hadoop_path)[0] or 'application/octet-stream'
    stats = request.fs.stats(hadoop_path)
    mtime = stats['mtime']
    size = stats['size']
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'), mtime, size):
        return HttpResponseNotModified()
        # TODO(philip): Ideally a with statement would protect from leaks,
    # but tricky to do here.
#     fh = request.fs.open(hadoop_path)
    fh = request.fs.do_as_superuser(request.fs.open, hadoop_path)

    response = HttpResponse(_file_reader(fh), content_type=content_type)
    response["Last-Modified"] = http_date(stats['mtime'])
    response["Content-Length"] = stats['size']
    response['Content-Disposition'] = request.GET.get('disposition', 'attachment')
    return response



def get_hadoop_path(request, path):

    path = Hdfs.normpath(path)

    project_home = get_project_dir(request.group.groupprofile.project)

    # 检查项目目录是否存在，不存在就创建
    ensure_project_directory(request.fs, request.group.groupprofile.project.slug)

    return project_home, os.path.join(project_home, path[1:])
    
