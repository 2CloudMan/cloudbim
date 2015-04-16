# coding=utf-8
from utils.lib.django_util import render
from django import forms


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

    pagenum = int(request.GET.get('pagenum', 1))
    pagesize = int(request.GET.get('pagesize', 30))

    data = {}



    return render('listdir.mako', request, data)


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




