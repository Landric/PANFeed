from django.conf.urls.defaults import patterns, include, url
from personalise.feed import PersonalFeed, IssueFeed
import settings

urlpatterns = patterns('personalise.views',
    url(r'^$','home', name='home'),
    url(r'^about/$','about', name='about'),
    url(r'^crawlme/$','crawlme', name='crawlme'),
    url(r'^urltoitem$','urltoitem', name='urltoitem'),

    url(r'^manageissue/$','manageissue', name='saveissue'),
    url(r'^manageissue/new/$','manageissue', name='newissue'),
    url(r'^manageissue/(?P<issueid>\d+)$','manageissue', name='manageissue'),
    url(r'^issuelist/$','issuelist', name='issuelist'),
    url(r'^issueitems/(?P<issueid>\d+)$','issueitems', name='issueitems'),

    url(r'submit/$', 'submit', name='submit'),

    url(r'^findnews/$','findnews', name='findnews'),
    url(r'^faq/$','faq', name='faq'),
)

urlpatterns += patterns('',
    url(r'^issue/(?P<issueid>\d+)$', IssueFeed(), name='issue'),
    url(r'^issue/(?P<issueid>\d+)/.*$', IssueFeed()),
    url(r'^find/(?P<sources>\w+)/(?P<keywords>\w+)/$', PersonalFeed()),
)
