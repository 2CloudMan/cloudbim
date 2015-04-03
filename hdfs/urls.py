from django.conf.urls import patterns, url

from hdfs import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)