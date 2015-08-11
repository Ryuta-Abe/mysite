from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mybook.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^cms/', include('cms.urls', namespace='cms')), 
    url(r'^pfv/', include('pfv.urls', namespace='pfv')),   # ←ここを追加
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static_site/(?P<path>.*)$','django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )