from django.db import models
from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import (
    AbstractBaseUser, UserManager, PermissionsMixin
)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'Usuário', 
        max_length=30, 
        unique=True,
        help_text='30 caracteres ou menos. Apenas letras, digitos e @/./+/-/_',
        validators=[username_validator],
    )
    email = models.EmailField('E-mail', unique=True)
    full_name = models.CharField('Nome completo', max_length=150, blank=True)
    is_active = models.BooleanField('Está ativo?', blank=True, default=True)
    is_staff = models.BooleanField('É da equipe?', blank=True, default=False)
    date_joined = models.DateTimeField('Data de entrada', auto_now_add=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    def __str__(self):
        # Returns the full name, otherwise return the username.
        return self.full_name or self.username
    
    def get_username(self):
        """Returns the username, use this instead CustomUser.username."""
        return self.username
    
    def get_short_name(self):
        """Returns the first part before space of the full name or the username."""
        return str(self).split(maxsplit=1)[0]
    
    def get_full_name(self):
        """Returns the full name or the username."""
        return str(self)


class PasswordReset(models.Model):
    """Informations about the reset on password made by users."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuário',
        related_name='resets',
    )
    token = models.CharField('Token', max_length=50, unique=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    confirmed = models.BooleanField('Confirmado?', blank=True, default=False)
    
    class Meta:
        verbose_name = 'reset de senha'
        verbose_name_plural = 'reset de senhas'
        ordering = ('-created_at',)
    
    def __str__(self):
        """User - creation date."""
        return f'{self.user} - {self.created_at}'
    
    def confirm(self):
        """Confirms the password reset, "invalidate" the token."""
        self.confirmed = True
        self.save() 