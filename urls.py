from django.conf.urls.defaults import patterns, include, url
from personalise.feed import PersonalFeed
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$','personalise.views.home', name='home'),
    url(r'^about/$','personalise.views.about', name='about'),
    url(r'^crawlme/$','personalise.views.crawlme', name='crawlme'),

    url(r'^find/(?P<keywords>\w+)/$', PersonalFeed()),
    
    # Examples:
    # url(r'^$', 'personal.views.home', name='home'),
    # url(r'^personal/', include('personal.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
     #url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
