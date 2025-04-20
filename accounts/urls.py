from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_settings, name='profile_settings'),
    path('security/', views.security_settings, name='security_settings'),
    path('toggle-2fa/', views.toggle_2fa, name='toggle_2fa'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/<uuid:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('dashboard/', views.dashboard, name='dashboard'),
]