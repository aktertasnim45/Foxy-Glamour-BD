from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Custom Registration View
    path('register/', views.register, name='register'),
    
    # Django's Built-in Login/Logout Views
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Password Change
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change_form.html',
        success_url='done/'
    ), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
]