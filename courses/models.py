from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from .utils import material_directory_path


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
    description = models.CharField('Descrição simples', max_length=250, blank=True)
    about = models.TextField('Sobre o curso', blank=True)
    start_date = models.DateField('Data de início', null=True, blank=True)
    image = models.ImageField(
        'Imagem', 
        upload_to='courses/images', 
        null=True, blank=True,
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    objects = CourseManager()

    class Meta:
        verbose_name = 'curso'
        verbose_name_plural = 'cursos'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def released_lessons(self):
        """Returns all lessons released."""
        today = timezone.now().date()
        return self.lessons.filter(release_date__gte=today)

    def get_absolute_url(self):
        """A url for a specific course."""
        return reverse('courses:details', args=(self.pk, self.slug))

    
class Lesson(models.Model):
    """A model for a lesson of a course."""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Curso',
        related_name='lessons',
    )
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição', blank=True)
    order = models.IntegerField('Ordem', blank=True, default=0)
    release_date = models.DateField('Data de liberação', blank=True, null=True)

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name='aula'
        verbose_name_plural = 'aulas'
        ordering = ('order',)
    
    def __str__(self):
        return self.name
    
    def is_available(self):
        """Returns True if a lesson is available. Otherwise returns False.
        
        A lesson is available if has the release date and the date is
        greater or equal today.
        The release date is set on admin site.
        """
        if self.release_date:
            today = timezone.now().date()
            return self.release_date >= today
        return False
    
    def get_absolute_url(self):
        """A url for a specific lesson."""
        return reverse(
            'courses:lesson_details', 
            args=(self.course.pk, self.course.slug, self.pk),
        )


class Material(models.Model):
    """A model for the material of a lesson."""
    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE,
        verbose_name='Aula',
        related_name='materials',
    )
    name = models.CharField('Nome', max_length=100)
    embedded = models.TextField('Vídeo da aula', blank=True)
    resource = models.FileField(
        'Recurso',
        upload_to=material_directory_path, 
        blank=True, null=True,
    )

    class Meta:
        verbose_name = 'material'
        verbose_name_plural = 'materiais'

    def __str__(self):
        return self.name
    
    def is_embedded(self):
        """Returns True if exists a embedded video."""
        return bool(self.embedded)


class Enrollment(models.Model):
    """A model for an enrollment for a course."""

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
        verbose_name_plural = 'inscrições'
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_enrollment')
        ]
    
    def __str__(self):
        return f'{self.user} - {self.course} - {self.EnrollmentStatus(self.status).label}'
    
    def approve(self):
        """Changes the enrollment status to approved."""
        self.status = self.EnrollmentStatus.APROVADO
        self.save()
    
    def is_approved(self):
        """Returns True if the user is approved."""
        return self.status == self.EnrollmentStatus.APROVADO


class Announcement(models.Model):
    """A model for an annoucement for a course."""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Curso',
        related_name='announcements',
    )
    title = models.CharField('Título', max_length=100)
    content = models.TextField('Conteúdo')

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'anúncio'
        verbose_name_plural = 'anúncios'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """A url for a specific announcement."""
        return reverse(
            'courses:announcement_details',
            args=(self.course.pk, self.course.slug, self.pk),
        )


class Comment(models.Model):
    """A model for comment in the announcement."""
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        verbose_name='Anúncio',
        related_name='comments',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name='Usuário',
        related_name='comments',
    )
    content = models.TextField('Comentário')

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'comentário'
        verbose_name_plural = 'comentários'
        ordering = ('created_at',)

    def __str__(self):
        if len(self.content) > 50:
            return f'{self.content[:50]}...'
        return self.content
    
    def get_absolute_url(self):
        """A url for a specific comment."""
        return reverse(
            'courses:edit_comment',
            args=(
                self.announcement.course.pk,
                self.announcement.course.slug,
                self.announcement.pk,
                self.pk,
            ),
        )