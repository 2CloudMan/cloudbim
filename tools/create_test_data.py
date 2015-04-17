# coding: utf-8
'''
Created on Apr 16, 2015

@author: linmiancheng
'''
from admin.models import Project, UserProfile, GroupProfile, GroupPermission, Role,\
        auth_models

DATA_STRUCT = [
               {
                   "project": 'cloudbim',
                   "role": 'provider'
                },
               {    
                    "project": 'webform',
                    'role': 'worker'
                },
               ]
def admin_init(group_detail):
    # create projects
    proj_name = group_detail.get('project', 'default')
    role_name = group_detail.get('role', 'default')
    project = Project(name=proj_name, project_directory='/project/cloudbim',
                       slug=proj_name)
    role = Role(name=role_name)
    
    group = auth_models.Group(name=proj_name+':'+role_name)
    project.save()
    role.save()
    group.save()
    
    gprofile = GroupProfile(group=group, role=role, project=project)
    user = auth_models.User.objects.filter(is_superuser=True).first()
    
    user.groups.add(group)
    gprofile.save()
    user.save()

if __name__ == "__main__":
    for item in DATA_STRUCT:
        admin_init(item)
