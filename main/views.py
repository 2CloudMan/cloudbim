# -*- coding=utf-8 -*-
from django.http.response import HttpResponse, HttpResponseRedirect
from utils.lib.exceptions_renderable import PopupException

import admin
from admin.models import get_profile, get_group_profile, get_user_proj_roles_info
from utils.lib.django_util import render
from utils.lib import paginator 
# Create your views here.

def index(request) :

    return listproj_paged(request)

def listproj_paged(request) :

    """
        分页显示项目列表
        user =  {
            'name': 'eric'
        }
        projects = [
        {
            'proj_name': 'haha'
        },
        {
            'proj_name': 'lala'
        }]
    """

    if request.user.is_authenticated():
        pagenum = int(request.GET.get('pagenum', 1))
        pagesize = int(request.GET.get('pagesize', 30))
        
        user =  {
            'name': request.user.username
        }
        
        projects = get_profile(request.user).get_projects()

        shown_projects = []
        if projects is not None:
            page = paginator.Paginator(projects, pagesize).page(pagenum)
            shown_projects =  [{'proj_name': project.name} for project in page.object_list]
        return render('listproj.mako', request, {
            'user': request.user,
            'projects': shown_projects
        })
    else:
        return HttpResponseRedirect('/auth/login')

def showproj(request, proj_slug) :
    role = get_profile(request.user).get_user_first_role(proj_slug)
    slug = role.slug
    return HttpResponseRedirect('/project/' + proj_slug + '/' + slug + '/')

def show(request, proj_slug, role_slug) :

    return info(request, proj_slug, role_slug)

def info(request, proj_slug, role_slug) :

    proj_info, roles_info = get_user_proj_roles_info(request.user, request.group.groupprofile.project)


    return render('info.mako', request, {
        'curr_proj': proj_slug,
        'curr_role': role_slug,
        'project': proj_info,
        'roles': roles_info,
    })

def profile(request):
    if request.user.is_authenticated():
        return render('profile.mako', request, {})
    else:
        return HttpResponseRedirect('/auth/login')


def history(request) :
    """
    pagesize:
    pagenum:
    query: 搜索关键字
    format:
    type: 请求log类型：【file/db】

    {
    records:[
        {
            'op':
            'time':
            'target':
            'type':[file|dir|table]
        }
    ],
    page:
    type:
    }

    """
    if request.user.is_authenticated():
        type = request.GET.get('type', '')
        query = request.GET.get('query', None)
        pagenum = int(request.GET.get('pagenum', 1))
        pagesize = int(request.GET.get('pagesize', 30))

        user_logs = get_profile(request.user).get_userlog(query, type)
        records = [dict(op=log.change_message ,time=log.action_time.strftime('%Y-%m-%d %H:%M:%S'),
                         target=log.object_repr) for log in user_logs]

        page = paginator.Paginator(records, pagesize).page(pagenum)
        page = _massage_page(page)

        return render('history.mako', request, dict(records=records, type=type,page=page))
    else:
        return HttpResponseRedirect('/auth/login')
    

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

