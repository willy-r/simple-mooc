from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.conf import settings


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
        verbose_name = 'curso'
        verbose_name_plural = 'cursos'
        ordering = ('name',)

    def __str__(self):
        """A string representation of course by the name."""
        return self.name
    
    def get_absolute_url(self):
        """A url for a specific course."""
        return reverse('courses:details', args=(self.pk, self.slug))


class Enrollment(models.Model):
    """A enrollment for a course from a user."""

    class EnrollmentStatus(models.IntegerChoices):        
        PENDENTE = 0
        APROVADO = 1
        CANCELADO = 2

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuário',
        related_name='enrollments',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Curso',
        related_name='enrollments',
    )
    status = models.IntegerField(
        'Situação', 
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.PENDENTE,
        blank=True,
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'inscrição'
        verbose_name_plural = 'incrições'
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_enrollment')
        ]
    
    def __str__(self):
        """Username - course name - status."""
        return f'{self.user} - {self.course} - {self.status.label}'