from django import forms
from django.forms import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, password_validation

from core.mail import send_mail_template

from .models import PasswordReset

user = get_user_model()


class CustomUserCreationForm(forms.ModelForm):
    """A custom form for creating new users with no privileges."""
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label='Confirmação de senha',
        widget=forms.PasswordInput,
        help_text='Repita a mesma senha digitada anteriormente, para verificação.'
    )

    class Meta:
        model = user
        fields = ('username', 'email')
    
    def clean_password2(self):
        # Check that the two password entries match.
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError('A confirmação não está correta.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class EditAccountForm(forms.ModelForm):
    """A form for updating the account information."""
    
    class Meta:
        model = user
        fields = ('username', 'email', 'full_name')


class CustomPasswordResetForm(forms.Form):
    """A custom password reset form to reset a user's password."""
    email = forms.EmailField(label='E-mail')

    def clean_email(self):
        # There's a user with this e-mail on db?
        email = self.cleaned_data['email']
        if not user.objects.filter(email=email).exists():
            raise ValidationError(
                'Nenhum usuário encontrado com este e-mail.'
            )
        return email
    
    def save(self, request=None, use_https=False):
        """Generate a one-use link for resetting password and send it."""
        email = self.cleaned_data['email']
        user_email = user.objects.get(email=email)
        token = default_token_generator.make_token(user_email)
        reset = PasswordReset(user=user_email, token=token)
        reset.save()
        
        subject = 'Criar nova senha no Simple MOOC'
        context = {
            'reset': reset,
            # Use get_current_site() because I have the request object.
            'domain': get_current_site(request).domain,
            'protocol': 'https' if use_https else 'http',
        }
        
        send_mail_template(
            subject,
            'accounts/password_reset_email.html',
            context,
            [user_email.email]
        )