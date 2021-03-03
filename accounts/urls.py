"""URL patterns for accounts app."""

from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'

urlpatterns = [
    # Ex: /conta/
    path('', views.dashboard, name='dashboard'),
    # Ex: /conta/editar/
    path('editar/', views.edit, name='edit'),
    # Ex: /conta/editar-senha/
    path('editar-senha/', views.edit_password, name='edit_password'),
    # Ex: /conta/nova-senha/
    path('nova-senha/', views.password_reset, name='password_reset'),
    # Ex: /conta/confirmar-nova-senha/<TOKEN>/
    path('confirmar-nova-senha/<str:token>/', 
         views.password_reset_confirm, 
         name='password_reset_confirm'),
    # Ex: /conta/entrar/
    path('entrar/',
         auth_views.LoginView.as_view(template_name='accounts/login.html'),
         name='login'),
    # Ex: /conta/sair/
    path('sair/', auth_views.LogoutView.as_view(), name='logout'),
    # Ex: /conta/registrar/
    path('cadastre-se/', views.register, name='register'),
]