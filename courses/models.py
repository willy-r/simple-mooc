from django.db import models
from django.db.models import Q
from django.urls import reverse


class CourseManager(models.Manager):
    """A custom manager for the class Course."""

    def search(self, query):
        """Filter courses by a specific query."""
        return self.get_queryset().filter(
           Q(name__icontains=query) | Q(description__icontains=query)
        )


class Course(models.Model):
    """A model for a course."""
    name = models.CharField('Nome', max_length=150)
    slug = models.SlugField('Atalho')
    description = models.TextField('Descrição simples', blank=True)
    about = models.TextField('Sobre o curso', blank=True)
    start_date = models.DateField('Data de início', null=True, blank=True)
    image = models.ImageField(
        'Imagem', 
        upload_to='courses/images', 
        null=True, blank=True
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    objects = CourseManager()

    class Meta:
        ordering = ('name',)
        verbose_name = 'curso'
        verbose_name_plural = 'cursos'

    def __str__(self):
        """A string representation of course by the name."""
        return self.name
    
    def get_absolute_url(self):
        """A url for a specific course."""
        return reverse('courses:details', args=(self.pk, self.slug))   