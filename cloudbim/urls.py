from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

from hdfs import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cloudbim.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('auth.urls')),
    url(r'^project/$', 'main.views.index', name='index'),
    url(r'^project/(?P<proj_slug>\w+)/$', 'main.views.showproj'),
    url(r'^project/(?P<proj_slug>\w+)/(?P<role_slug>\w+)/$', 'main.views.info'),
    url(r'^project/(?P<proj_slug>\w+)/(?P<role_slug>\w+)/info$', 'main.views.info'),
    url(r'^project/(?P<proj_slug>\w+)/(?P<role_slug>\w+)/fb/', include('hdfs.urls')),
    url(r'^project/(?P<proj_slug>\w+)/(?P<role_slug>\w+)/tb/', include('hbase.urls')),
)
