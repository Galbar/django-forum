from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ForumSite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include('Forum.urls'), {'forum_id':0}),
    url(r'^(?P<forum_id>\d+)/', include('Forum.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
