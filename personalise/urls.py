from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView
from personalise.feed import PersonalFeed, UserFeed
import settings

urlpatterns = patterns('personalise.views',
    url(r'^$',         TemplateView.as_view(template_name="index.html"),name='home'),
    url(r'^about/$',   TemplateView.as_view(template_name="about.html"),name='about'),
    url(r'^crawlme/$', TemplateView.as_view(template_name="crawlme.html"),name='crawlme'),
    url(r'^findnews/$',TemplateView.as_view(template_name="findnews.html"), name='findnews'),
    url(r'^faq/$',     TemplateView.as_view(template_name="faq.html"), name='faq'),
    
    url(r'^urltoitem$','urltoitem', name='urltoitem'),

    url(r'^publishnews/$','publishnews', name='publishnews'),

    url(r'^managefeed/$','managefeed', name='savefeed'),
    url(r'^managefeed/new/$','managefeed', name='newfeed'),
    url(r'^managefeed/(?P<feed_id>\d+)$','managefeed', name='managefeed'),

    url(r'submit/$', 'submit', name='submit'),
)

urlpatterns += patterns('',
    url(r'^issue/(?P<issueid>\d+)$', UserFeed(), name='issue'),
    url(r'^issue/(?P<issueid>\d+)/.*$', UserFeed()),
    url(r'^find/(?P<sources>\w+)/(?P<keywords>\w+)/$', PersonalFeed()),
)
