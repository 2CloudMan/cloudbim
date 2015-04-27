from django.conf.urls import patterns, include, url

from django.contrib import admin

# Django expects handler404 and handler500 to be defined.
# django.conf.urls provides them. But we want to override them.
# Also see http://code.djangoproject.com/ticket/5350
handler404 = 'utils.views.serve_404_error'
handler500 = 'utils.views.serve_500_error'

admin.autodiscover()

from hdfs import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cloudbim.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'auth.views.dt_login'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('auth.urls')),
    url(r'^project/$', 'main.views.index', name='index'),
    url(r'^project/(?P<proj_slug>\w+)/$', 'main.views.showproj'),
    url(r'^project/(?P<proj_slug>\w+)/(?P<role_slug>\w+)/$', 'main.views.info'),
    url(r'^project/(?P<proj_slug>\w+)/(?P<role_slug>\w+)/info$', 'main.views.info'),
    url(r'^project/(?P<proj_slug>\w+)/(?P<role_slug>\w+)/fb/', include('hdfs.urls')),
    url(r'^project/(?P<proj_slug>\w+)/(?P<role_slug>\w+)/tb/', include('hbase.urls')),
)
