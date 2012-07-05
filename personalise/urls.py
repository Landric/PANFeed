from django.conf.urls.defaults import patterns, include, url
from personalise.feed import PersonalFeed, DigestFeed, IssueFeed
import settings

urlpatterns = patterns('',
    url(r'^$','personalise.views.home', name='home'),
    url(r'^about/$','personalise.views.about', name='about'),
    url(r'^crawlme/$','personalise.views.crawlme', name='crawlme'),
    url(r'^urltoitem$','personalise.views.urltoitem', name='urltoitem'),

    url(r'^managedigest/$','personalise.views.managedigest', name='savedigest'),
    url(r'^managedigest/new/$','personalise.views.managedigest', name='newdigest'),
    url(r'^managedigest/(?P<digestid>\d+)$','personalise.views.managedigest', name='managedigest'),
    url(r'^digestlist/$','personalise.views.digestlist', name='digestlist'),
    url(r'^digest/(?P<digestid>\w+)$', DigestFeed()),

    url(r'^createissue/$','personalise.views.createissue', name='createissue'),
    url(r'^manageissue/(?P<issueid>\w+)$','personalise.views.manageissue', name='manageissue'),
    url(r'^issuelist/$','personalise.views.issuelist', name='issuelist'),
    url(r'^saveissue/$','personalise.views.saveissue', name='saveissue'),
    url(r'^issueitems/(?P<issueid>\w+)$','personalise.views.issueitems', name='issueitems'),
    url(r'^issue/(?P<issueid>\w+)$', IssueFeed()),
    url(r'^issue/(?P<issueid>\w+)/.*$', IssueFeed()),

    url(r'^find/(?P<sources>\w+)/(?P<keywords>\w+)/$', PersonalFeed()),
    url(r'submit/$', 'personalise.views.submit', name='submit'),

    url(r'^findnews/$','personalise.views.findnews', name='findnews'),
    url(r'^faq/$','personalise.views.faq', name='faq'),
)
