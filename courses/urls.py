"""URL patterns for courses app."""

from django.urls import path

from . import views


app_name = 'courses'

urlpatterns = [
    # Ex: /cursos/
    path('', views.index, name='index'),
    # Ex: /cursos/1/
    path('<int:pk>/<str:slug>/', views.details, name='details'),
]