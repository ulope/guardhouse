from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
from main.views import SiteListView, SiteDetailView, SiteVerifyView, SiteDeleteView, SiteCreateView, SiteUpdateView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'guardhouse.views.home', name='home'),
    # url(r'^guardhouse/', include('guardhouse.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^$', 'content.views.home', name="home"),
    url(r'^dashboard/$', 'main.views.dashboard', name="dashboard"),

    url(r'^settings/$', 'main.views.settings', name="settings"),

    url(r'^account/setup/$', 'main.views.account_setup', name="account_setup"),
    url(r'^account/setup/(?P<force>[a-z]+)/$', 'main.views.account_setup', name="account_setup"),

    url(r'^sites/$', SiteListView.as_view(), name="sites"),
    url(r'^sites/add/$', SiteCreateView.as_view(), name="site_create"),
    url(r'^sites/(?P<pk>[0-9]+)/$', SiteDetailView.as_view(), name="site_detail"),
    url(r'^sites/(?P<pk>[0-9]+)/edit/$', SiteUpdateView.as_view(), name="site_edit"),
    url(r'^sites/(?P<pk>[0-9]+)/verify/$', SiteVerifyView.as_view(), name="site_verify"),
    url(r'^sites/(?P<pk>[0-9]+)/delete/$', SiteDeleteView.as_view(), name="site_delete"),

    url(r'^content/', include("content.urls")),

    url(r'^auth/login/$', 'django.contrib.auth.views.login', name="login"),
    url(r'^auth/logout/$', 'django.contrib.auth.views.logout', name="logout"),
    url(r'^auth/register/$', 'django.contrib.auth.views.logout', name="logout"),
    url(r'^auth/', include('social_auth.urls')),

    url(r'^receiver/$', 'sentry_wrap.views.store', name="receiver"),

    url(r'^sentry/', include("sentry.web.urls")),

    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATICFILES_DIRS[0]}),
    )
