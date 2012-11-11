from django.conf import settings
from django.conf.urls import patterns, include, url
from translations.urls import translation_patterns
from yawdtrans_demo.views import IndexView, MultilingualPageView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^elfinder/', include('elfinder.urls'))
)

#insert the url translatable patterns
urlpatterns += translation_patterns('',
    url(r'^$', IndexView.as_view(), name='index-view'),
    url(r'^(?P<slug>[\w-]+)/$', MultilingualPageView.as_view(), name='multilingual-page-view'),
)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, }),
    )
