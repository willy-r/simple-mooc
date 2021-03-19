from datetime import date, timedelta

from django.core import mail
from django.urls import reverse
from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model

from model_bakery import baker


class IndexViewTests(TestCase):

    def test_view_url_accessible_at_desired_location(self):
        response = self.client.get('/cursos/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('courses:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('courses:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/index.html')
    
    def test_view_no_courses(self):
        response = self.client.get(reverse('courses:index'))
        self.assertEqual(response.status_code, 200)

        # If no courses available on the platform, displays an appropriate message.
        self.assertContains(response, 'Nenhum curso está disponível na plataforma.')
        self.assertQuerysetEqual(response.context['courses'], [])
    
    def test_view_two_courses(self):
        baker.make('courses.Course', name='Curso de Teste', _quantity=2)
        response = self.client.get(reverse('courses:index'))
        self.assertEqual(response.status_code, 200)
        
        # May display multiple courses.
        self.assertEqual(response.context['courses'].count(), 2)
        self.assertQuerysetEqual(
            response.context['courses'],
            ['<Course: Curso de Teste>', '<Course: Curso de Teste>']
        )


class CourseDetailsViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up data that will be used on the entirily class.
        cls.course = baker.make('courses.Course', slug='curso-de-teste')

    def test_view_url_accessible_at_desired_location(self):
        response = self.client.get('/cursos/1/curso-de-teste/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('courses:details', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('courses:details', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/details.html')
    
    def test_view_HTTP404_not_found_course(self):
        # pk=2 and slug='not-found' does not exists. 
        response = self.client.get(reverse('courses:details', args=(2, 'not-found')))
        self.assertEqual(response.status_code, 404)
    
    def test_view_redirects_on_form_confirmation(self):
        data = {'name': 'Teste', 'email': 'teste@teste.com', 'message': 'Teste'}
        path = reverse('courses:details', args=(self.course.pk, self.course.slug))
        response = self.client.post(path, data, follow=True)

        # Redirects to the same page.
        self.assertRedirects(response, reverse('courses:details', args=(self.course.pk, self.course.slug)))

        # Test the sending message on form confirmation.
        message = list(response.context['messages'])[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'Seu e-mail foi enviado com sucesso!')
    
    def test_form_error_missing_fields(self):
        data = {'name': '', 'email': '', 'message': ''}
        path = reverse('courses:details', args=(self.course.pk, self.course.slug))
        response = self.client.post(path, data)
        self.assertEqual(response.status_code, 200)
        
        # Display an appropriate message if the field was not filled.
        fields = ['name', 'email', 'message']
        for field in fields:
            self.assertFormError(response, 'form', field, 'Este campo é obrigatório.')
    
    def test_form_error_invalid_email(self):
        data = {'name': 'Teste', 'email': 'testeteste', 'message': 'Teste'}
        path = reverse('courses:details', args=(self.course.pk, self.course.slug))
        response = self.client.post(path, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', 'Informe um endereço de email válido.')
    
    def test_form_valid_data_send_mail(self):
        data = {'name': 'Teste', 'email': 'teste@teste.com', 'message': 'Teste'}
        path = reverse('courses:details', args=(self.course.pk, self.course.slug))
        response = self.client.post(path, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify if the e-mail was sent successfully.
        self.assertEqual(len(mail.outbox), 1)
    
    def test_email_was_sent_to_correct_receiver(self):
        data = {'name': 'Teste', 'email': 'teste@teste.com', 'message': 'Teste'}
        path = reverse('courses:details', args=(self.course.pk, self.course.slug))
        response = self.client.post(path, data)
        self.assertListEqual(mail.outbox[0].to, [settings.CONTACT_EMAIL])
    
    def test_email_was_sent_from_the_correct_sender(self):
        data = {'name': 'Teste', 'email': 'teste@teste.com', 'message': 'Teste'}
        path = reverse('courses:details', args=(self.course.pk, self.course.slug))
        response = self.client.post(path, data)
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)


class MakeEnrollmentViewTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.course = baker.make('courses.Course', slug='curso-de-teste')
        # User to use on the entirily class.
        cls.user = get_user_model().objects.create_user(username='user', password='123')

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('courses:enrollment', args=(self.course.pk, self.course.slug)))
        self.assertRedirects(response, '/conta/entrar/?next=/cursos/1/curso-de-teste/inscreva-se/')
    
    def test_view_url_accessible_at_desired_location(self):
        self.client.login(username='user', password='123')
        response = self.client.get('/cursos/1/curso-de-teste/inscreva-se/')
        self.assertEqual(response.status_code, 302)
    
    def test_view_url_accessible_by_name(self):
        self.client.login(username='user', password='123')
        response = self.client.get(reverse('courses:enrollment', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 302)
    
    def test_view_redirects_to_final_destination(self):
        self.client.login(username='user', password='123')
        url = reverse('courses:enrollment', args=(self.course.pk, self.course.slug))
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('accounts:dashboard'))
    
    def test_view_HTTP404_not_found_course(self):
        # To make enrollment on a course, must exist a course.
        self.client.login(username='user', password='123')
        response = self.client.get(reverse('courses:enrollment', args=(2, 'not-found')))
        self.assertEqual(response.status_code, 404)
    
    def test_view_make_enrollment_on_course(self):
        # Test the view functionallity on success.
        self.client.login(username='user', password='123')
        url = reverse('courses:enrollment', args=(self.course.pk, self.course.slug))
        response = self.client.get(url, follow=True)
        
        # Verify if there is a enrollment on the course for the user logged in.
        # Must have one enrollment and that enrollment must have the status approved.
        enrollments = self.course.enrollments.filter(user=self.user)
        self.assertTrue(enrollments[0].is_approved())
        self.assertEqual(enrollments.count(), 1)
        
        # After make enrollment on a course, an appropriate message is displayed.
        message = list(response.context['messages'])[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, f'Você foi inscrito no curso "{self.course}" com sucesso!')
    
    def test_view_already_has_enrollment(self):
        # Test the view functionallity if a user already has an enrollment.
        self.client.login(username='user', password='123')
        baker.make('courses.Enrollment', course=self.course, user=self.user)
        url = reverse('courses:enrollment', args=(self.course.pk, self.course.slug))
        response = self.client.get(url, follow=True)
        
        # Get all the enrollments of the logged user, then verify if the user has
        # more than one enrollment for the course.
        enrollments = self.course.enrollments.filter(user=self.user)
        self.assertNotEqual(enrollments.count(), 2)
        
        # After trying to make an enrollment on a course, if a user already has an enrollment
        # on that course, an appropriate message is displayed.
        message = list(response.context['messages'])[0]
        self.assertEqual(message.tags, 'info')
        self.assertEqual(message.message, f'Você já está inscrito no curso "{self.course}".')  
    

class EnrollmentRequiredDecoratorTests(TestCase):
    """Test the enrollment_required decorator.
    
    Uses the view undo_enrollment() for this, this decorator will be used
    on others views with the same functionallity.
    """

    @classmethod
    def setUpTestData(cls):
        cls.course = baker.make('courses.Course', slug='curso-de-teste')
        cls.user = get_user_model().objects.create_user(username='user', password='123')
        cls.superuser = get_user_model().objects.create_superuser(
            username='superuser', email='teste@teste.com', password='123',
        )

    def test_HTTP404_not_found_course(self):
        self.client.login(username='user', password='123')
        response = self.client.get(reverse('courses:undo_enrollment', args=(2, 'not-found')))
        self.assertEqual(response.status_code, 404)
    
    def test_redirects_if_not_has_enrollment(self):
        self.client.login(username='user', password='123')
        url = reverse('courses:undo_enrollment', args=(self.course.pk, self.course.slug))
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('accounts:dashboard'))

        # If the user not has enrollment, an appropriate message is displayed.
        message = list(response.context['messages'])[0]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(message.message, 'Desculpe, mas você não tem permissão para acessar esta página.')
    
    def test_redirects_if_has_enrollment_not_approved(self):
        self.client.login(username='user', password='123')
        enrollment = baker.make('courses.Enrollment', course=self.course, user=self.user)
        url = reverse('courses:undo_enrollment', args=(self.course.pk, self.course.slug))
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('accounts:dashboard'))

        # Check if the enrollment is approved (status=1).
        self.assertFalse(enrollment.is_approved())
        
        # If the user has enrollment, but the status of that enrollment is pendent,
        # an appropriate message is displayed.
        message = list(response.context['messages'])[0]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(message.message, 'A sua inscrição no curso ainda está pendente.')
        
    def test_superuser_access_without_enrollment(self):
        self.client.login(username='superuser', password='123')
        response = self.client.get(reverse('courses:undo_enrollment', args=(self.course.pk, self.course.slug)))
        self.assertTrue(response.context['user'].is_staff)
        self.assertEqual(response.status_code, 200)


class UndoEnrollmentViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.course = baker.make('courses.Course', slug='curso-de-teste')
        cls.user = get_user_model().objects.create_user(username='user', password='123')
        # To undo and enrollment, the user must have one.
        baker.make('courses.Enrollment', course=cls.course, user=cls.user, status=1)
        cls.superuser = get_user_model().objects.create_superuser(
            username='superuser', email='teste@teste.com', password='123',
        )
    
    def test_view_redirects_iuserlogged_in(self):
        response = self.client.get(reverse('courses:undo_enrollment', args=(self.course.pk, self.course.slug)))
        self.assertRedirects(response, '/conta/entrar/?next=/cursos/1/curso-de-teste/cancelar/')
    
    def test_view_url_accessible_at_desired_location(self):
        self.client.login(username='user', password='123')
        response = self.client.get('/cursos/1/curso-de-teste/cancelar/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        self.client.login(username='user', password='123')
        response = self.client.get(reverse('courses:undo_enrollment', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        self.client.login(username='user', password='123')
        response = self.client.get(reverse('courses:undo_enrollment', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/undo_enrollment.html')
    
    def test_undo_enrollment_on_course(self):
        # Test the view functionallity on success.
        self.client.login(username='user', password='123')
        url = reverse('courses:undo_enrollment', args=(self.course.pk, self.course.slug))
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('accounts:dashboard'))
        
        # Verify if there is no enrollment on the course for the user logged in.
        # Must have no enrollment.
        enrollments = self.course.enrollments.filter(user=self.user)
        self.assertEqual(enrollments.count(), 0)
        
        # After user undo the enrollment, an appropriate message is displayed.
        message = list(response.context['messages'])[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'Sua inscrição foi cancelada com sucesso!')
    
    def test_view_HTTP404_superuser_without_enrollment(self):
        # Gambiarra thing.
        self.client.login(username='superuser', password='123')
        response = self.client.post(reverse('courses:undo_enrollment', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 404)


class AnnouncementsViewTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.course = baker.make('courses.Course', slug='curso-de-teste')
        cls.user = get_user_model().objects.create_user(username='user', password='123')
        baker.make('courses.Enrollment', course=cls.course, user=cls.user, status=1)
    
    def test_view_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('courses:announcements', args=(self.course.pk, self.course.slug)))
        self.assertRedirects(response, '/conta/entrar/?next=/cursos/1/curso-de-teste/anuncios/')
    
    def test_view_url_accessible_at_desired_location(self):
        self.client.login(username='user', password='123')
        response = self.client.get('/cursos/1/curso-de-teste/anuncios/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        self.client.login(username='user', password='123')
        response = self.client.get(reverse('courses:announcements', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        self.client.login(username='user', password='123')
        response = self.client.get(reverse('courses:announcements', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/announcements.html')
    
    def test_view_no_announcements(self):
        self.client.login(username='user', password='123')
        response = self.client.get(reverse('courses:announcements', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhum anúncio criado.')
        self.assertQuerysetEqual(response.context['announcements'], [])
    
    def test_view_two_announcements(self):
        # May display multiple announcements.
        self.client.login(username='user', password='123')
        baker.make('courses.Announcement', course=self.course, title='Anuncio de Teste', _quantity=2)
        response = self.client.get(reverse('courses:announcements', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['announcements'].count(), 2)
        self.assertQuerysetEqual(
            response.context['announcements'],
            ['<Announcement: Anuncio de Teste>', '<Announcement: Anuncio de Teste>'],
        )


class AnnouncementDetailsViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.course = baker.make('courses.Course', slug='curso-de-teste')
        cls.announcement = baker.make('courses.Announcement', course=cls.course)
        cls.user = get_user_model().objects.create_user(username='user', password='123')
        baker.make('courses.Enrollment', course=cls.course, user=cls.user, status=1)
    
    def test_view_redirects_if_not_logged_in(self):
        url = reverse('courses:announcement_details', args=(self.course.pk, self.course.slug, self.announcement.pk))
        response = self.client.get(url)
        self.assertRedirects(response, '/conta/entrar/?next=/cursos/1/curso-de-teste/anuncios/1/')
    
    def test_view_url_accessible_at_desired_location(self):
        self.client.login(username='user', password='123')
        response = self.client.get('/cursos/1/curso-de-teste/anuncios/1/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        self.client.login(username='user', password='123')
        url = reverse('courses:announcement_details', args=(self.course.pk, self.course.slug, self.announcement.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        self.client.login(username='user', password='123')
        url = reverse('courses:announcement_details', args=(self.course.pk, self.course.slug, self.announcement.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/announcement_details.html')
    
    def test_view_HTTP404_not_found_announcement(self):
        self.client.login(username='user', password='123')
        url = reverse('courses:announcement_details', args=(self.course.pk, self.course.slug, 2))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_view_redirects_on_form_confirmation(self):
        self.client.login(username='user', password='123')
        data = {'content': 'Teste'}
        path = reverse('courses:announcement_details', args=(self.course.pk, self.course.slug, self.announcement.pk))
        response = self.client.post(path, data, follow=True)

        # Redirects to the same page.
        expected = reverse(
            'courses:announcement_details', 
            args=(self.course.pk, self.course.slug, self.announcement.pk),
        )
        self.assertRedirects(response, expected)
        
        # Check if the comment was added on the announcement successfully.
        self.assertEqual(self.announcement.comments.all().count(), 1)

        # Test the sending message on form confirmation.
        message = list(response.context['messages'])[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'Seu comentário foi enviado.')
    
    def test_form_error_missing_field(self):
        self.client.login(username='user', password='123')
        data = {'content': ''}
        path = reverse('courses:announcement_details', args=(self.course.pk, self.course.slug, self.announcement.pk))
        response = self.client.post(path, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'content', 'Este campo é obrigatório.')
    
    def test_view_no_comments(self):
        self.client.login(username='user', password='123')
        url = reverse('courses:announcement_details', args=(self.course.pk, self.course.slug, self.announcement.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Seja o primeiro a comentar!')
        self.assertQuerysetEqual(response.context['comments'], [])
    
    def test_view_two_comments(self):
        self.client.login(username='user', password='123')
        # Add two comments.
        baker.make('courses.Comment', content='Teste', announcement=self.announcement, _quantity=2)
        url = reverse('courses:announcement_details', args=(self.course.pk, self.course.slug, self.announcement.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.announcement.comments.all().count(), 2)
        self.assertQuerysetEqual(
            response.context['comments'],
            ['<Comment: Teste>', '<Comment: Teste>'],
        )


class EditCommentViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.course = baker.make('courses.Course', slug='curso-de-teste')
        cls.announcement = baker.make('courses.Announcement', course=cls.course)
        cls.user1 = get_user_model().objects.create_user(username='user1', password='123')
        cls.user2 = get_user_model().objects.create_user(username='user2', email='teste@teste.com', password='123')
        cls.comment = baker.make('courses.Comment', announcement=cls.announcement, user=cls.user1)
        # The users must have enrollment to access.
        baker.make('courses.Enrollment', course=cls.course, user=cls.user1, status=1)
        baker.make('courses.Enrollment', course=cls.course, user=cls.user2, status=1)
    
    def test_view_redirect_if_not_logged_in(self):
        url = reverse(
            'courses:edit_comment', 
            args=(self.course.pk, self.course.slug, self.announcement.pk, self.comment.pk),
        )
        response = self.client.get(url)
        self.assertRedirects(
            response,
            '/conta/entrar/?next=/cursos/1/curso-de-teste/anuncios/1/editar-comentario/1/',
        )
    
    def test_view_url_accessible_at_desired_location(self):
        self.client.login(username='user1', password='123')
        response = self.client.get('/cursos/1/curso-de-teste/anuncios/1/editar-comentario/1/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        self.client.login(username='user1', password='123')
        url = reverse(
            'courses:edit_comment', 
            args=(self.course.pk, self.course.slug, self.announcement.pk, self.comment.pk),
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='123')
        url = reverse(
            'courses:edit_comment', 
            args=(self.course.pk, self.course.slug, self.announcement.pk, self.comment.pk),
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/edit_comment.html')
    
    def test_view_HTTP404_not_found_announcement(self):
        self.client.login(username='user1', password='123')
        # There is only one announcement, the pk=2 does not exists.
        url = reverse('courses:edit_comment', args=(self.course.pk, self.course.slug, 2, self.comment.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_view_HTTP404_not_found_comment(self):
        self.client.login(username='user1', password='123')
        # There is only one comment, the pk=2 does not exists.
        url = reverse('courses:edit_comment', args=(self.course.pk, self.course.slug, self.announcement.pk, 2))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_view_HTTP404_not_comment_owner(self):
        # This user not is the comment owner, and will try to access the page to edit the comment.
        self.client.login(username='user2', password='123')
        url = reverse(
            'courses:edit_comment', 
            args=(self.course.pk, self.course.slug, self.announcement.pk, self.comment.pk),
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_redirects_on_form_confirmation(self):
        # Test the form functionallity on success.
        self.client.login(username='user1', password='123')
        data = {'content': f'{self.comment.content} editado'}
        url = reverse(
            'courses:edit_comment', 
            args=(self.course.pk, self.course.slug, self.announcement.pk, self.comment.pk),
        )
        response = self.client.post(url, data, follow=True)
        expected = reverse(
            'courses:announcement_details', 
            args=(self.course.pk, self.course.slug, self.announcement.pk),
        )
        self.assertRedirects(response, expected)

        # Test if the comment was successfully edited.
        before = self.comment.content
        after = response.context['comments'].get(pk=self.comment.pk).content
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(before, after)
        self.assertContains(response, after)

        # Test the message sending on the form confirmation.
        message = list(response.context['messages'])[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'Seu comentário foi editado com sucesso.')
    
    def test_form_error_missing_field(self):
        self.client.login(username='user1', password='123')
        data = {'content': ''}
        path = reverse(
            'courses:edit_comment', 
            args=(self.course.pk, self.course.slug, self.announcement.pk, self.comment.pk),
        ) 
        response = self.client.post(path, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'content', 'Este campo é obrigatório.')


class LessonsViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.course = baker.make('courses.Course', slug='curso-de-teste')
        cls.user = get_user_model().objects.create_user(username='user', password='123')
        cls.superuser = get_user_model().objects.create_superuser(
            username='superuser', email='teste@teste.com',  password='123',
        )
        baker.make('courses.Enrollment', course=cls.course, user=cls.user, status=1)

    def test_view_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('courses:lessons', args=(self.course.pk, self.course.slug)))
        self.assertRedirects(response, '/conta/entrar/?next=/cursos/1/curso-de-teste/aulas/')
    
    def test_view_url_accessible_at_desired_location(self):
        self.client.login(username='user', password='123')
        response = self.client.get('/conta/entrar/?next=/cursos/1/curso-de-teste/aulas/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        self.client.login(username='user', password='123')
        response = self.client.get(reverse('courses:lessons', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        self.client.login(username='user', password='123')
        response = self.client.get(reverse('courses:lessons', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/lessons.html')
    
    def test_view_no_lessons(self):
        self.client.login(username='user', password='123')
        response = self.client.get(reverse('courses:lessons', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhuma aula disponível.')
        self.assertQuerysetEqual(response.context['lessons'], [])
    
    def test_view_past_lesson(self):
        # Lessons with a release_date in the past are displayed.
        self.client.login(username='user', password='123')
        past_lesson = date.today() + timedelta(days=-1)
        baker.make('courses.Lesson', course=self.course, name='Aula do Passado', release_date=past_lesson)
        response = self.client.get(reverse('courses:lessons', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['lessons'], ['<Lesson: Aula do Passado>'])
    
    def test_view_future_lesson(self):
        # Lessons with a release_date in the future aren't displayed.
        self.client.login(username='user', password='123')
        future_lesson = date.today() + timedelta(days=1)
        baker.make('courses.Lesson', course=self.course, name='Aula do Futuro', release_date=future_lesson)
        response = self.client.get(reverse('courses:lessons', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhuma aula disponível.')
        self.assertQuerysetEqual(response.context['lessons'], [])
    
    def test_view_past_and_future_lesson(self):
        # Even if both past and future lessons exist, only past questions are displayed.
        self.client.login(username='user', password='123')

        # Create lessons.
        past_date = date.today() + timedelta(days=-1)
        future_date = date.today() + timedelta(days=1)
        baker.make('courses.Lesson', course=self.course, name='Aula do Passado', release_date=past_date)
        baker.make('courses.Lesson', course=self.course, name='Aula do Futuro', release_date=future_date)
        
        response = self.client.get(reverse('courses:lessons', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['lessons'], ['<Lesson: Aula do Passado>'])
    
    def test_view_two_lessons_superuser(self):
        # Lessons with release_date in past and future are displayed for superuser.
        self.client.login(username='superuser', password='123')

        # Create lessons.
        past_date = date.today() + timedelta(days=-1)
        future_date = date.today() + timedelta(days=1)
        baker.make('courses.Lesson', course=self.course, release_date=past_date)
        baker.make('courses.Lesson', course=self.course, release_date=future_date)
        
        response = self.client.get(reverse('courses:lessons', args=(self.course.pk, self.course.slug)))
        self.assertEqual(response.status_code, 200)

        # Confirm that the user is a superuser, then verify if has two lessons.
        self.assertTrue(response.context['user'].is_staff)
        self.assertEqual(response.context['lessons'].count(), 2)

        # Lesson without a release_date are displayed for a superuser too.
        baker.make('courses.Lesson', course=self.course, name='Aula de Teste')
        response = self.client.get(reverse('courses:lessons', args=(self.course.pk, self.course.slug)))
        self.assertContains(response, '(Agendado: Sem previsão)')
        self.assertQuerysetEqual(response.context['lessons'].filter(pk=3), ['<Lesson: Aula de Teste>'])


class LessonDetailsViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.course = baker.make('courses.Course', slug='curso-de-teste')
        past_date = date.today() + timedelta(days=-1)
        cls.lesson_available = baker.make('courses.Lesson', course=cls.course, release_date=past_date)
        cls.user = get_user_model().objects.create_user(username='user', password='123')
        baker.make('courses.Enrollment', course=cls.course, user=cls.user, status=1)

    def test_view_redirect_if_not_logged_in(self):
        url = reverse('courses:lesson_details', args=(self.course.pk, self.course.slug, self.lesson_available.pk))
        response = self.client.get(url)
        self.assertRedirects(response, '/conta/entrar/?next=/cursos/1/curso-de-teste/aulas/1/')
    
    def test_view_url_accessible_at_desired_location(self):
        self.client.login(username='user', password='123')
        response = self.client.get('/cursos/1/curso-de-teste/aulas/1/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        self.client.login(username='user', password='123')
        url = reverse('courses:lesson_details', args=(self.course.pk, self.course.slug, self.lesson_available.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        self.client.login(username='user', password='123')
        url = reverse('courses:lesson_details', args=(self.course.pk, self.course.slug, self.lesson_available.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/lesson_details.html')
    
    def test_view_HTTP404_not_found_lesson(self):
        self.client.login(username='user', password='123')
        # There are two lessons, so pk=3 does not exists.
        url = reverse('courses:lesson_details', args=(self.course.pk, self.course.slug, 3))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_view_redirects_lesson_unvailable(self):
        # Lesson is unvailable if no has a release_date or the date is in the future.
        self.client.login(username='user', password='123')
        lesson_unvailable = baker.make('courses.Lesson', course=self.course)
        url = reverse('courses:lesson_details', args=(self.course.pk, self.course.slug, lesson_unvailable.pk))
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('courses:lessons', args=(self.course.pk, self.course.slug)))
        
        # If the lesson is unvailable, an appropriate message is displayed.
        message = list(response.context['messages'])[0]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(message.message, 'Esta aula não está disponível.')
        
    def test_view_no_materials(self):
        self.client.login(username='user', password='123')
        url = reverse('courses:lesson_details', args=(self.course.pk, self.course.slug, self.lesson_available.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['lesson'].materials.all().count(), 0)
        self.assertContains(response, 'Não disponível.')
    
    def test_view_three_materials_broken_link(self):
        self.client.login(username='user', password='123')
        # Creates three materials.
        baker.make('courses.Material', lesson=self.lesson_available, name='Material de Teste', _quantity=3)
        url = reverse('courses:lesson_details', args=(self.course.pk, self.course.slug, self.lesson_available.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Materials without url or resource are displayed, but with a broken link.
        material = response.context['lesson'].materials.get(pk=1)

        # Verify if material has no url or resource.
        self.assertFalse(material.is_embedded())
        self.assertFalse(material.resource)

        # Three materials with broken link, so must have three 'Link Quebrado' on the page.
        self.assertContains(response, 'Link Quebrado', count=3)
        self.assertQuerysetEqual(
            response.context['lesson'].materials.order_by('name'),
            ['<Material: Material de Teste>', '<Material: Material de Teste>', '<Material: Material de Teste>'],
        )


class MaterialDetailsViewTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.course = baker.make('courses.Course', slug='curso-de-teste')
        past_date = date.today() + timedelta(days=-1)
        cls.lesson_available = baker.make('courses.Lesson', course=cls.course, release_date=past_date)
        cls.material_embedded = baker.make(
            'courses.Material', url='https://www.youtube.com/embed/Mp0vhMDI7fA', lesson=cls.lesson_available,
        )
        cls.user = get_user_model().objects.create_user(username='user', password='123')
        cls.enrollment = baker.make('courses.Enrollment', course=cls.course, user=cls.user, status=1)

    def test_view_redirect_if_not_logged_in(self):
        url = reverse('courses:material_details', args=(self.course.pk, self.course.slug, self.material_embedded.pk))
        response = self.client.get(url)
        self.assertRedirects(response, '/conta/entrar/?next=/cursos/1/curso-de-teste/aulas/materiais/1/')
    
    def test_view_url_accessible_at_desired_location(self):
        self.client.login(username='user', password='123')
        response = self.client.get('/cursos/1/curso-de-teste/aulas/materiais/1/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        self.client.login(username='user', password='123')
        url = reverse('courses:material_details', args=(self.course.pk, self.course.slug, self.material_embedded.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        self.client.login(username='user', password='123')
        url = reverse('courses:material_details', args=(self.course.pk, self.course.slug, self.material_embedded.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/material_details.html')
    
    def test_view_HTTP404_not_found_material(self):
        self.client.login(username='user', password='123')
        url = reverse('courses:material_details', args=(self.course.pk, self.course.slug, 4))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_view_redirects_no_embedded_video(self):
        self.client.login(username='user', password='123')
        # Creates a material without url.
        material = baker.make('courses.Material', lesson=self.lesson_available)
        url = reverse('courses:material_details', args=(self.course.pk, self.course.slug, material.pk))
        response = self.client.get(url, follow=True)
        expected = reverse(
            'courses:lesson_details', 
            args=(self.course.pk, self.course.slug, self.lesson_available.pk),
        )
        self.assertRedirects(response, expected)

        # Verify if the material has no embedded video.
        material = response.context['lesson'].materials.get(pk=material.pk)
        self.assertFalse(material.is_embedded())

        # If the material has no embedded video an appropriate message is displayed.
        message = list(response.context['messages'])[0]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(message.message, 'Esta aula não possui um vídeo disponível, tente um dos recursos abaixo.')
    
    def test_view_redirects_material_unvailable(self):
        # Material is unvailable if the lesson of the material is unvailable.
        # And a lesson is unvailable if no has release_date or the date is in the future.
        self.client.login(username='user', password='123')
        lesson_unvailable = baker.make('courses.Lesson', course=self.course)
        material = baker.make('courses.Material', lesson=lesson_unvailable)
        url = reverse('courses:material_details', args=(self.course.pk, self.course.slug, material.pk))
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('courses:lessons', args=(self.course.pk, self.course.slug)))
        
        # If the material is unvailable, an appropriate message is displayed.
        message = list(response.context['messages'])[0]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(message.message, 'Este material não está disponível.')