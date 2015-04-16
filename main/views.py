# coding=utf-8
from utils.lib.django_util import render
from django.http.response import HttpResponse, HttpResponseRedirect

# Create your views here.

def index(request) :

    return listproj_paged(request)

def listproj_paged(request) :

    """
        分页显示项目列表
    """

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
    return render('listproj.mako', request, {
        'user': user,
        'projects': projects
    })


def showproj(request, proj_slug) :

    return HttpResponseRedirect('/project/' + proj_slug + '/designer/')

def show(request, proj_slug, role_slug) :

    return info(request, proj_slug, role_slug)

def info(request, proj_slug, role_slug) :

    return render('info.mako', request, {

    })
