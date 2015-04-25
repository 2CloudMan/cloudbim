# coding: utf-8
'''
Created on Apr 16, 2015

@author: linmiancheng
'''
from admin.models import Project, GroupProfile, Role,\
        auth_models, FileInfo, BimFilePermission
from django.db.backends.dummy.base import IntegrityError
from django.conf import settings
DATA_STRUCT = [
               {
                   "project": 'cloudbim',
                   "role": 'provider'
                },
               {    
                    "project": 'webform',
                    'role': 'worker',
                    "file_perm": [{
                                  "path": settings.HADOOP_PROJECT_DIR + 'webform/worker',
                                  "perm": 'rwx',
                                  },
                                  ]
                },
               ]
def admin_init(group_detail):
    # create projects
    proj_name = group_detail.get('project', 'default')
    role_name = group_detail.get('role', 'default')
    
    try:
        role = Role(name=role_name, slug=role_name)
        role.save()
        print 'role %s created' % role.name
    except IntegrityError:
        role = Role.objects.get(name=role_name)
    
    try:
        group = auth_models.Group(name=proj_name+':'+role_name)
        group.save()
        print 'group %s created' % group.name
    except IntegrityError:
        group = auth_models.Group.objects.get(name=proj_name+':'+role_name)
    
    user = auth_models.User.objects.filter(is_superuser=True).first()

    try:
        project = Project(name=proj_name, project_directory=settings.HADOOP_PROJECT_DIR+proj_name,
                           slug=proj_name, manager=user)
        project.save()
        print 'project created'
    except IntegrityError:
        project = Project.objects.get(name=proj_name)
    
    try:
        gprofile = GroupProfile(group=group, role=role, project=project)
        user.groups.add(group)
        gprofile.save()
        user.save()
    except:
        pass

    if 'file_perm' in group_detail:
        for perm in group_detail.get('file_perm'):
            print perm
            try:
                file_ifo = FileInfo(path=perm.get('path'), owner=user, group=group)
                file_ifo.save()
            except IntegrityError:
                file_ifo = FileInfo.objects.get(path=perm.get('path'))
            try: 
                perm = BimFilePermission(file=file_ifo, action=perm.get('perm'), creator=user)
                perm.groups.add(group)
                perm.save()
                print 'permission <%s-%s-%s>created!' % (group.name, file_ifo.path, perm.action)
            except:
                pass
            
            
def all_init():
    for item in DATA_STRUCT:
        admin_init(item)


if __name__ == "__main__":
    print 'Data initial starting!'
    all_init()
    print 'Finish!'
