from django.forms import Textarea
from django.test import SimpleTestCase

from courses.forms import ContactCourseForm


class ContactCourseFormTests(SimpleTestCase):

    def setUp(self):
        # Create a unbound form that will be used in every test.
        self.form = ContactCourseForm()

    def test_form_name_field(self):
        self.assertEqual(self.form.fields['name'].label, 'Nome')
        self.assertEqual(self.form.fields['name'].max_length, 100)
    
    def test_form_email_field(self):
        self.assertEqual(self.form.fields['email'].label, 'E-mail')
    
    def test_form_message_field(self):
        self.assertEqual(self.form.fields['message'].label, 'Mensagem/Dúvida')
        self.assertIsInstance(self.form.fields['message'].widget, Textarea)
    
    def test_form_valid_data_send_mail(self):
        self.skipTest('Already tested in `courses.tests.test_views.CourseDetailsViewTests`')
        pass
