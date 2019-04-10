from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#import app.forms
import app.views

from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path('signup/', app.views.signup, name='signup'),
    path('resetpassword/', auth_views.PasswordResetView.as_view(template_name='registration/resetpassword.html'), name="resetpassword"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/resetpasswordconfirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/resetpasswordcomplete.html'), name='password_reset_complete'),

    path('upload', app.views.upload, name='upload'),
    path('download', app.views.download_zip),
    path('display', app.views.displayImages, name='displayImages'),
    path('', app.views.gallery, name = 'gallery'),

    re_path(r'^(?P<slug>[-\w]+)$', app.views.AlbumDetail.as_view(), name='album'),

    # Auth related urls
    path('accounts/login/$', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/$', app.views.logout, name='logout'),

    # Uncomment the next line to enable the admin:
    path('admin/', admin.site.urls),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'app.views.handler404'
