from utils.lib.django_util import render
from django.http.response import HttpResponse, HttpResponseRedirect

# Create your views here.

def home(request) :

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
    return render('home.mako', request, {
        'user': user,
        'projects': projects
    })

def showproj(request, proj_name) :

    return HttpResponseRedirect('/project/' + proj_name + '/designer/')

def show(request, proj_name, role_name) :

    return HttpResponse(proj_name)

def info(request) :

    return
