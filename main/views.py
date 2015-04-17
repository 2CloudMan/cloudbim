# -*- coding=utf-8 -*-
from django.http.response import HttpResponse, HttpResponseRedirect

import admin
from admin.models import get_profile, get_group_profile
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
        page = paginator.Paginator(projects, pagesize).page(pagenum)
        shown_projects =  [{'proj_name': project.name} for project in page.object_list]
        
        return render('listproj.mako', request, {
            'user': user,
            'projects': shown_projects
        })
    else:
        return HttpResponseRedirect('/auth/login')

def showproj(request, proj_slug) :

    return HttpResponseRedirect('/project/' + proj_slug + '/designer/')

def show(request, proj_slug, role_slug) :

    return info(request, proj_slug, role_slug)

def info(request, proj_slug, role_slug) :

    return render('info.mako', request, {

    })
