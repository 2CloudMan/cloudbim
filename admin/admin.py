from django.contrib import admin

from .models import Project, UserProfile, GroupPermission, GroupProfile,  Role,\
        BimFilePermission, BimHbasePermission
# Register your models here.
admin.site.register(Project)
admin.site.register(UserProfile)
admin.site.register(GroupPermission)
admin.site.register(GroupProfile)
admin.site.register(Role)
admin.site.register(BimFilePermission)
admin.site.register(BimHbasePermission)