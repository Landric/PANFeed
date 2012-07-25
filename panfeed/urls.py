from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView, ListView
from panfeed.feed import PersonalFeed, UserFeed
from panfeed.models import AcademicFeeds,Feed,FeedItem
from panfeed.views import FindNews, FeedListView, PublishNews
from tastypie.api import Api
from panfeed.api import FeedResource, FeedItemResource, SpecialIssueResource

v2_api = Api(api_name='v2')
v2_api.register(FeedResource())
v2_api.register(FeedItemResource())
v2_api.register(SpecialIssueResource())

urlpatterns = patterns('panfeed.views',
    url(r'^$',         TemplateView.as_view(template_name="index.html"),name='home'),
    url(r'^about/$',   TemplateView.as_view(template_name="about.html"),name='about'),
    url(r'^crawlme/$', TemplateView.as_view(template_name="crawlme.html"),name='crawlme'),
    url(r'^faq/$',     TemplateView.as_view(template_name="faq.html"), name='faq'),
    
    url(r'^urltoitem$','urltoitem', name='urltoitem'),
    
    url(r'^findnews/$',         FindNews.as_view(),     name='findnews'),
    url(r'^findnews/allfeeds$', FeedListView.as_view(), name='allfeeds'),
    url(r'^publishnews/$',      PublishNews.as_view(),  name='publishnews'),

    url(r'^managefeed/(?P<feed_id>\d+)/manageitem/new$','manageitem', name='newitem'),
    url(r'^managefeed/(?P<feed_id>\d+)/manageitem/(?P<item_id>\d+)$','manageitem', name='manageitem'),

    url(r'^managefeed/new/$','managefeed', name='newfeed'),
    url(r'^managefeed/(?P<feed_id>\d+)$','managefeed', name='managefeed'),



    url(r'submit/$', 'submit', name='submit'),
)

urlpatterns += patterns('',
    url(r'^issue/(?P<issueid>\d+)$', UserFeed(), name='issue'),
    url(r'^issue/(?P<issueid>\d+)/.*$', UserFeed()),
    url(r'^find$', PersonalFeed(), name="find"),
)
