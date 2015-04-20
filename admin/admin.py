from django.contrib import admin

from .models import Project, UserProfile, GroupProfile,  Role,\
        BimFilePermission, BimHbasePermission, auth_models, FileInfo, TableInfo

from .forms import GroupProfileForm
        
class GroupProfileAdmin(admin.ModelAdmin):
    
    form = GroupProfileForm


# Register your models here.
admin.site.register(Project)
admin.site.register(UserProfile)
# admin.site.register(GroupPermission)
admin.site.register(GroupProfile, GroupProfileAdmin)
admin.site.register(Role)
admin.site.register(FileInfo)
admin.site.register(TableInfo)
admin.site.register(BimFilePermission)
admin.site.register(BimHbasePermission)