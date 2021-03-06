"""URL patterns for courses app."""

from django.urls import path

from . import views


app_name = 'courses'

urlpatterns = [
    # Ex: /cursos/
    path('', views.index, name='index'),
    # Ex: /cursos/1/<SLUG>/
    path('<int:pk>/<slug:slug>/', views.details, name='details'),
    # Ex: /cursos/1/<SLUG>/aulas/
    path('<int:pk>/<slug:slug>/aulas/', views.lessons, name='lessons'),
    # Ex: /cursos/1/<SLUG>/aulas/1/
    path('<int:pk>/<slug:slug>/aulas/<int:lesson_pk>/', 
         views.lesson_details, 
         name='lesson_details'),
	# Ex: /cursos/1/<SLUG>/aulas/materiais/1/
    path('<int:pk>/<slug:slug>/aulas/materiais/<int:material_pk>/', 
         views.material_details, 
         name='material_details'),
    # Ex: /cursos/1/<SLUG>/inscreva-se/
    path('<int:pk>/<slug:slug>/inscreva-se/', 
         views.make_enrollment, 
         name='enrollment'),
    # Ex: /cursos/1/<SLUG>/cancelar/
    path('<int:pk>/<slug:slug>/cancelar/',
         views.undo_enrollment,
         name='undo_enrollment'),
    # Ex: /cursos/1/<SLUG>/anuncios/
    path('<int:pk>/<slug:slug>/anuncios/', 
         views.announcements, 
         name='announcements'),
    # Ex: /cursos/1/<SLUG>/anuncios/1/
    path('<int:pk>/<slug:slug>/anuncios/<int:announcement_pk>/', 
         views.announcement_details, 
         name='announcement_details'),
    # Ex: /cursos/1/<SLUG>/anuncios/1/editar-comentario/1/
    path('<int:pk>/<slug:slug>/anuncios/<int:announcement_pk>/editar-comentario/<int:comment_pk>/', 
         views.edit_comment, 
         name='edit_comment'),
]