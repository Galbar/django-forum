# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from Forum import views

urlpatterns = patterns('',
    url(r'^$', views.forum, name='base_forum'),
    url(r'^page/(?P<page>\d+)/$', views.forum),
    url(r'^subforum/(?P<subforum_id>\d+)[\w\d@\.\+\-_]*/$', views.subforum, name='subforum'),
    url(r'^subforum/(?P<subforum_id>\d+)[\w\d@\.\+\-_]*/page/(?P<page>\d+)/$', views.subforum, name='subforum'),
    url(r'^subforum/(?P<subforum_id>\d+)[\w\d@\.\+\-_]*/post/$', views.newThread),
    url(r'^subforum/(?P<subforum_id>\d+)[\w\d@\.\+\-_]*/new-subforum/$', views.newSubforum),
    url(r'^thread/(?P<thread_id>\d+)[\w\d@\.\+\-_]*/page/last/$', views.thread, {'go_last_page': True}, name='thread_last_page'),
    url(r'^thread/(?P<thread_id>\d+)[\w\d@\.\+\-_]*/$', views.thread, name='thread'),
    url(r'^thread/(?P<thread_id>\d+)[\w\d@\.\+\-_]*/page/(?P<page>\d+)/$', views.thread, name='thread'),
    url(r'^thread/(?P<thread_id>\d+)[\w\d@\.\+\-_]*/post/$', views.replyThread),
    url(r'^post/(?P<post_id>\d+)/edit/$', views.editPost),
    url(r'^post/(?P<post_id>\d+)/report/$', views.reportPost),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),

)
