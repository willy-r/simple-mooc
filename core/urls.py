"""URL patterns for core app."""

from django.urls import path

from . import views


app_name = 'core'

urlpatterns = [
    # Ex: /
    path('', views.home, name='home'),
    # Ex: /contato/
    path('contato/', views.contact, name='contact'),
]