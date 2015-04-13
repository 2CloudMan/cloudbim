from utils.lib.django_util import render


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