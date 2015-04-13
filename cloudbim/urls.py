from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

from hdfs import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cloudbim.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^hdfs/', include('hdfs.urls')),
    url(r'^auth/', include('auth.urls')),
    url(r'^project/$', 'main.views.home', name='home'),
    #url(r'^project/(?P<proj_name>\w+)/$', 'main.views.showproj'),
    #url(r'^project/(?P<proj_name>\w+)/(?P<role_name>\w+)/$', 'main.view.show'),
    #url(r'^project/(?P<proj_name>\w+)/(?P<role_name>\w+)/fb$', 'hdfs.view.index'),
    #url(r'^project/(?P<proj_name>\w+)/(?P<role_name>\w+)/fb/view(?P<path>/.*)/.$', 'hdfs.view.view'),
    #url(r'^project/(?P<proj_name>\w+)/(?P<role_name>\w+)/fb/listdir(?P<path>/.*)/.$', 'hdfs.view.view'),
)
