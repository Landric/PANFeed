from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView, ListView
from panfeed.feed import PersonalFeed, UserFeed
from panfeed.models import AcademicFeeds,Feed,FeedItem
from panfeed.views import FindNews, FeedListView, PublishNews, UserUpdateView

urlpatterns = patterns('panfeed.views',
    url(r'^$',         TemplateView.as_view(template_name="index.html"),name='home'),
    url(r'^about/$',   TemplateView.as_view(template_name="about.html"),name='about'),
    url(r'^crawlme/$', TemplateView.as_view(template_name="crawlme.html"),name='crawlme'),
    url(r'^faq/$',     TemplateView.as_view(template_name="faq.html"), name='faq'),
    
    url(r'^urltoitem$','urltoitem', name='urltoitem'),

    url(r'^findnews/$',         FindNews.as_view(),     name='findnews'),
    url(r'^findnews/allfeeds$', FeedListView.as_view(), name='allfeeds'),
    url(r'^publishnews/$',      PublishNews.as_view(),  name='publishnews'),

    url(r'^manageitem/(?P<feed_slug>[\w-]+)/$','manageitem', name='newitem'),
    url(r'^manageitem/(?P<feed_slug>[\w-]+)/(?P<item_slug>[\w-]+)$','manageitem', name='manageitem'),

    url(r'^managefeed/(?P<feed_slug>[\w-]+)/manageissue/$','manageissue', name='newissue'),
    url(r'^managefeed/(?P<feed_slug>[\w-]+)/manageissue/(?P<issue_slug>[\w-]+)$','manageissue', name='manageissue'),

    url(r'^managefeed/$','managefeed', name='newfeed'),
    url(r'^managefeed/(?P<feed_slug>[\w-]+)$','managefeed', name='managefeed'),

    url(r'^user/(?P<slug>[\w-]+)$', UserUpdateView.as_view(), name='profile'),

    url(r'submit/$', 'submit', name='submit'),
)

urlpatterns += patterns('',
    url(r'^feed/(?P<feed_slug>[\w-]+)$', UserFeed(), name='viewfeed'),
    url(r'^find$', PersonalFeed(), name="find"),
)
