from django.conf.urls.defaults import patterns, include, url
from personalise.feed import PersonalFeed, DigestFeed, IssueFeed
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$','personalise.views.home', name='home'),
    url(r'^about/$','personalise.views.about', name='about'),
    url(r'^crawlme/$','personalise.views.crawlme', name='crawlme'),
    url(r'^urltoitem$','personalise.views.urltoitem', name='urltoitem'),

    url(r'^managedigest/$','personalise.views.managedigest', name='savedigest'),
    url(r'^managedigest/new/$','personalise.views.managedigest', name='newdigest'),
    url(r'^managedigest/(?P<digestid>\d+)$','personalise.views.managedigest', name='managedigest'),
    url(r'^digestlist/$','personalise.views.digestlist', name='digestlist'),
    url(r'^digest/(?P<digestid>\d+)$', DigestFeed()),

    url(r'^manageissue/$','personalise.views.manageissue', name='saveissue'),
    url(r'^manageissue/new/$','personalise.views.manageissue', name='newissue'),
    url(r'^manageissue/(?P<issueid>\d+)$','personalise.views.manageissue', name='manageissue'),
    url(r'^issuelist/$','personalise.views.issuelist', name='issuelist'),
    url(r'^issueitems/(?P<issueid>\d+)$','personalise.views.issueitems', name='issueitems'),
    url(r'^issue/(?P<issueid>\d+)$', IssueFeed()),
    url(r'^issue/(?P<issueid>\d+)/.*$', IssueFeed()),

    url(r'^find/(?P<sources>\w+)/(?P<keywords>\w+)/$', PersonalFeed()),
    url(r'submit/$', 'personalise.views.submit', name='submit'),

    url(r'^findnews/$','personalise.views.findnews', name='findnews'),
    url(r'^faq/$','personalise.views.faq', name='faq'),

#    url(r'^password_required/$', 'password_required.views.login'),    
    # Examples:
    # url(r'^$', 'personal.views.home', name='home'),
    # url(r'^personal/', include('personal.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^account/', include('registration.urls')),
    url(r'^account/login_redirect', 'personalise.views.login_redirect'),

)
