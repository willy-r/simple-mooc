"""Forms for the courses app."""

from django import forms
from django.conf import settings
from django.core.mail import send_mail

from core.mail import send_mail_template


class ContactCourseForm(forms.Form):
    """Contact form to know more about a course."""
    name = forms.CharField(label='Nome', max_length=100)
    email = forms.EmailField(label='E-mail')
    message = forms.CharField(label='Mensagem/Dúvida', widget=forms.Textarea)

    def send_mail(self, course):
        """Sends an e-mail."""
        subject = f'[{course.name}] Contato'
        context = {
            'name': self.cleaned_data['name'],
            'email': self.cleaned_data['email'],
            'message': self.cleaned_data['message'],
        }
        send_mail_template(
            subject,
            'courses/contact_email.html',
            context,
            [settings.CONTACT_EMAIL],
        )