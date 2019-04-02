from django.urls import path
from.import views
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = [
   path('login/', LoginView.as_view(template_name='registration/login.html'), name="login"),
   path('logout/', LogoutView.as_view(template_name='upload.html'), name="logout"),
   path('signup/', views.signup, name='signup'),
   path('resetpassword/', PasswordResetView.as_view(template_name='registration/resetpassword.html'), name="resetpassword"),
   path('password_reset/done/', PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
   path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/resetpasswordconfirm.html'), name='password_reset_confirm'),
   path('reset/done/', PasswordResetCompleteView.as_view(template_name='registration/resetpasswordcomplete.html'), name='password_reset_complete')
]
