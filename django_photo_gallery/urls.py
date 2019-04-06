from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#import app.forms
import app.views

from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path('', include('app.urls')),
    path('upload', app.views.upload, name='upload'),
    path('display', app.views.displayImages, name='displayImages'),
    url(r'^$', app.views.gallery, name='gallery'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/icons/favicon.ico', permanent=True)),
    url(r'^(?P<slug>[-\w]+)$', app.views.AlbumDetail.as_view(), name='album'),  # app.views.AlbumView.as_view()

    # Auth related urls
    url(r'^accounts/login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', app.views.logout, {'next_page': '/', }, name='logout'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'app.views.handler404'
