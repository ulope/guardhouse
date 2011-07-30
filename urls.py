from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'guardhouse.views.home', name='home'),
    # url(r'^guardhouse/', include('guardhouse.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^$', 'content.views.home', name="home"),

    url(r'^login/', lambda x: x, name="login"),
    url(r'^signup/', lambda x: x, name="signup"),

    url(r'^content/', include("content.urls")),

    url(r'^admin/', include(admin.site.urls)),
)
