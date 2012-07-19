from django.conf.urls.defaults import patterns, include, url
from personalise.feed import PersonalFeed, UserFeed
import settings

urlpatterns = patterns('personalise.views',
    url(r'^$','home', name='home'),
    url(r'^about/$','about', name='about'),
    url(r'^crawlme/$','crawlme', name='crawlme'),
    url(r'^urltoitem$','urltoitem', name='urltoitem'),

    url(r'^publishnews/$','publishnews', name='publishnews'),

    url(r'^managefeed/$','managefeed', name='savefeed'),
    url(r'^managefeed/new/$','managefeed', name='newfeed'),
    url(r'^managefeed/(?P<feedid>\d+)$','managefeed', name='managefeed'),

    url(r'submit/$', 'submit', name='submit'),

    url(r'^findnews/$','findnews', name='findnews'),
    url(r'^faq/$','faq', name='faq'),
)

urlpatterns += patterns('',
    url(r'^issue/(?P<issueid>\d+)$', UserFeed(), name='issue'),
    url(r'^issue/(?P<issueid>\d+)/.*$', UserFeed()),
    url(r'^find/(?P<sources>\w+)/(?P<keywords>\w+)/$', PersonalFeed()),
)
