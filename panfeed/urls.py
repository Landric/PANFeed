from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView, ListView
from panfeed.feed import PersonalFeed, UserFeed
from panfeed.models import AcademicFeeds,Feed,FeedItem
from panfeed.views import FindNews, FeedListView, PublishNews, UserUpdateView

urlpatterns = patterns('panfeed.views',
    url(r'^$',         TemplateView.as_view(template_name="panfeed/index.html"),name='home'),
    url(r'^about/$',   TemplateView.as_view(template_name="panfeed/about.html"),name='about'),
    url(r'^crawlme/$', TemplateView.as_view(template_name="panfeed/crawlme.html"),name='crawlme'),
    url(r'^faq/$',     TemplateView.as_view(template_name="panfeed/faq.html"), name='faq'),
    
    url(r'^urltoitem$','urltoitem', name='urltoitem'),

    url(r'^news/$',         FindNews.as_view(),     name='findnews'),
    url(r'^news/allfeeds/$', FeedListView.as_view(), name='allfeeds'),

    url(r'^feed/(?P<feed_slug>[\w-]+)/item/(?P<item_slug>[\w-]+)?$','manageitem', name='manageitem'),
    url(r'^feed/(?P<feed_slug>[\w-]+)/issue/(?P<issue_slug>[\w-]+)?$','manageissue', name='manageissue'),
    url(r'^feed/$',      PublishNews.as_view(),  name='publishnews'),
    url(r'^feed/(?P<feed_slug>[\w-]+)?$','managefeed', name='managefeed'),

    url(r'^user/(?P<slug>[\w-]+)$', UserUpdateView.as_view(), name='profile'),

    url(r'submit/$', 'submit', name='submit'),
)

urlpatterns += patterns('',
    url(r'^rssfeed/(?P<feed_slug>[\w-]+)$', UserFeed(), name='viewfeed'),
    url(r'^find$', PersonalFeed(), name="find"),
)
