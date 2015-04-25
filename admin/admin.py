from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from .models import Project, UserProfile, GroupProfile,  Role,\
        BimFilePermission, BimHbasePermission, auth_models, FileInfo, TableInfo

from .forms import GroupProfileForm
        
class GroupProfileAdmin(admin.ModelAdmin):
    
    form = GroupProfileForm


class GroupAdmin(GroupAdmin):
    pass
#     filter_horizontal = ()
#     exclude = ('permissions',)

class PermissionAdmin(admin.ModelAdmin):
    filter_horizontal = ('groups',)


# Unregister Group models
admin.site.unregister(auth_models.Group)
# Register your models here.
admin.site.register(auth_models.Group, GroupAdmin)
admin.site.register(Project)
admin.site.register(UserProfile)
# admin.site.register(GroupPermission)
admin.site.register(GroupProfile, GroupProfileAdmin)
admin.site.register(Role)
admin.site.register(FileInfo)
admin.site.register(TableInfo)
admin.site.register(BimFilePermission, PermissionAdmin)
admin.site.register(BimHbasePermission, PermissionAdmin)
