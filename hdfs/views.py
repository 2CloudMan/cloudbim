# coding=utf-8
from utils.lib.django_util import render
from utils.lib.exceptions_renderable import PopupException
from utils.hadoop.fs.hadoopfs import Hdfs
from utils.lib import paginator
from django import forms

import posixpath
import stat
import logging
from datetime import datetime


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
    # 判断给定路径是否是一个目录
    if not request.fs.isdir(path):
        Log.warn('user %s try to open a dir user the given path %s but it is not a directory!' %
                (request.user.username, path)) 
        raise PopupException("Not a directory: %s" % (path,))
    
    # 判断给定的路径是否是在用户所在的目录下

    # 用户是否有查看目录的权限
    if request.user.is_superuser or request.user.has_file_permission(path, 'r'):
        pagenum = int(request.GET.get('pagenum', 1))
        pagesize = int(request.GET.get('pagesize', 30))
        
        breadcrumbs = parse_breadcrumbs(path)
        dir_list = request.fs.do_as_user(request.user.name, request.fs.listdir_stats, path)
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
            'path': path,
            'raw_path': '',
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
    return {
        'name': stats.get('name', ''),
        'path': normalized,
        'raw_path': '/project_slug/role_slug/mydir/mywork',
        'permission': '???',
        'human_size': '12kb',
        'project': 'proj_slug',
        'role':  'role_slug',
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

    if request.method == 'POST':
        pass


    return

