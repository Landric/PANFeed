from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api
from panfeed.api.resources import FeedResource, FeedItemResource, SpecialIssueResource

v2_api = Api(api_name='v2')
v2_api.register(FeedResource())
v2_api.register(FeedItemResource())
v2_api.register(SpecialIssueResource())

urlpatterns = patterns('',
    url(
        r'favicon\.ico$',
        RedirectView.as_view(
            url = settings.STATIC_URL + 'images/favicon.ico',
            permanent = False
        ),
        name="favicon"
    ),
    url(r'', include('panfeed.urls')),
#    url(r'^password_required/$', 'password_required.views.login'),    
    # Examples:
    # url(r'^$', 'personal.views.home', name='home'),
    # url(r'^personal/', include('personal.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^csp', include('csp.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('django_browserid.urls')),
    #url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^sign-out/$', 'django.contrib.auth.views.logout', name="logout"),
    url(r'^sign-in/$', 'django.contrib.auth.views.login', name="login")
    (r'^api/', include(v1_api.urls)),
)
