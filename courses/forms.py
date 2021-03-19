"""Forms for the courses app."""

from django import forms
from django.conf import settings

from core.mail import send_mail_template

from .models import Comment


class ContactCourseForm(forms.Form):
    """Contact form to know more about a course."""
    name = forms.CharField(label='Nome', max_length=100)
    email = forms.EmailField(label='E-mail')
    message = forms.CharField(label='Mensagem/Dúvida', widget=forms.Textarea)

    def send_mail(self, course=None):
        """Sends an e-mail."""
        subject = f'[{course}] Contato'
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


class CommentForm(forms.ModelForm):
    """A form for a user add a comment on a announcement."""

    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
        }
    
    def save(self, user, announcement, commit=True):
        comment = super().save(commit=False)
        comment.user = user
        comment.announcement = announcement
        if commit:
            comment.save()
        return comment