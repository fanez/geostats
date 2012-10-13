from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'world.views.index'),
    url(r'^stats/(?P<region>\D+)/(?P<indicator>\S+)$', 'world.views.countries'),
)
