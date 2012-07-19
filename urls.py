from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
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
    #url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^account/', include('registration.urls')),
    url(r'^account/login_redirect', 'panfeed.views.login_redirect'),

)
