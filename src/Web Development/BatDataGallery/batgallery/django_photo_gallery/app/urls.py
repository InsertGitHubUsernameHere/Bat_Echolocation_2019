from django.urls import path
from.import views
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView

urlpatterns = [
   path('login/', LoginView.as_view(template_name='registration/login.html'), name="login"),
   path('logout/', LogoutView.as_view(template_name='upload.html'), name="logout"),
   path('signup/', views.signup, name='signup'),
   path('resetpassword/', PasswordResetView, name="resetpassword")
]
