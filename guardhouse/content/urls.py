from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^impressum/$', 'content.views.impressum', name="impressum"),
)
