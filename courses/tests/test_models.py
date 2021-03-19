from datetime import date, timedelta

from django.test import TestCase

from model_bakery import baker

from courses.models import Course


class CourseModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.course = baker.make('courses.Course', name='Curso de Teste', slug='curso-de-teste')
        cls.fields = {field.name: field for field in cls.course._meta.get_fields()}
    
    def test_name_field(self):
        self.assertEqual(self.fields['name'].verbose_name, 'Nome')
        self.assertEqual(self.fields['name'].max_length, 150)

    def test_slug_field(self):
        self.assertEqual(self.fields['slug'].verbose_name, 'Atalho')
        self.assertEqual(self.fields['slug'].max_length, 50)
    
    def test_description_field(self):
        self.assertEqual(self.fields['description'].verbose_name, 'Descrição simples')
        self.assertEqual(self.fields['description'].max_length, 250)
        self.assertTrue(self.fields['description'].blank)
    
    def test_about_field(self):
        self.assertEqual(self.fields['about'].verbose_name, 'Sobre o curso')
        self.assertTrue(self.fields['about'].blank)
    
    def test_start_date_field(self):
        self.assertEqual(self.fields['start_date'].verbose_name, 'Data de início')
        self.assertTrue(self.fields['start_date'].blank)
        self.assertTrue(self.fields['start_date'].null)
    
    def test_image_field(self):
        self.assertEqual(self.fields['image'].verbose_name, 'Imagem')
        self.assertEqual(self.fields['image'].upload_to, 'courses/images')
        self.assertTrue(self.fields['image'].blank)
        self.assertTrue(self.fields['image'].null)
        self.assertEqual(
            self.fields['image'].help_text, 
            'Use uma imagem com as dimensões 400 x 250.',
        )
    
    def test_created_at_field(self):
        self.assertEqual(self.fields['created_at'].verbose_name, 'Criado em')
        self.assertTrue(self.fields['created_at'].auto_now_add)
        self.assertFalse(self.fields['created_at'].editable)
    
    def test_updated_at_field(self):
        self.assertEqual(self.fields['updated_at'].verbose_name, 'Atualizado em')
        self.assertTrue(self.fields['updated_at'].auto_now)
        self.assertFalse(self.fields['updated_at'].editable)
    
    def test_objects_search_by_name(self):
        baker.make('courses.Course', name='Curso de Teste com Django', _quantity=10)
        search = Course.objects.search('django')
        self.assertEqual(search.count(), 10)

    def test_objects_search_by_description(self):
        baker.make('courses.Course', description='Curso de Django', _quantity=10)
        search = Course.objects.search('django')
        self.assertEqual(search.count(), 10)
    
    def test_objects_search_no_courses(self):
        baker.make('courses.Course', name='Curso Teste de Django', description='Curso de Django', _quantity=10)
        search = Course.objects.search('not found')
        self.assertEqual(search.count(), 0)
    
    def test_meta_class(self):
        self.assertEqual(self.course._meta.verbose_name, 'curso')
        self.assertEqual(self.course._meta.verbose_name_plural, 'cursos')
        self.assertTupleEqual(self.course._meta.ordering, ('name',))
    
    def test_object_name(self):
        self.assertEqual(str(self.course), 'Curso de Teste')
    
    def test_get_absolute_url_is_correct(self):
        expected = '/cursos/1/curso-de-teste/'
        self.assertURLEqual(self.course.get_absolute_url(), expected)
    
    def test_released_lessons(self):
        # Create lessons.
        present_date = date.today()
        past_date = present_date + timedelta(days=-1)
        future_date = present_date + timedelta(days=1)
        baker.make('courses.Lesson', course=self.course, release_date=present_date)
        baker.make('courses.Lesson', course=self.course, release_date=past_date)
        baker.make('courses.Lesson', course=self.course, release_date=future_date)
        
        # Verify if return only released lessons.
        # A lesson is considerated released if has release_date <= today.
        self.assertEqual(self.course.released_lessons().count(), 2)


class LessonModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        course = baker.make('courses.Course', slug='curso-de-teste')
        cls.lesson = baker.make('courses.Lesson', course=course, name='Aula de Teste')
        cls.fields = {field.name: field for field in cls.lesson._meta.get_fields()}
    
    def test_course_field(self):
        self.assertEqual(self.fields['course'].verbose_name, 'Curso')

    def test_name_field(self):
        self.assertEqual(self.fields['name'].verbose_name, 'Nome')
        self.assertEqual(self.fields['name'].max_length, 100)
    
    def test_description_field(self):
        self.assertEqual(self.fields['description'].verbose_name, 'Descrição')
        self.assertTrue(self.fields['description'].blank)
    
    def test_order_field(self):
        self.assertEqual(self.fields['order'].verbose_name, 'Ordem')
        self.assertTrue(self.fields['order'].unique)
        self.assertEqual(self.fields['order'].help_text, 'Ordem de liberação da aula, começando do 1.')
        self.assertEqual(self.fields['order'].error_messages['unique'], 'Aula com esta ordem já existe.')

    def test_release_date_field(self):
        self.assertEqual(self.fields['release_date'].verbose_name, 'Data de liberação')
        self.assertTrue(self.fields['release_date'].blank)
        self.assertTrue(self.fields['release_date'].null)
        self.assertEqual(
            self.fields['release_date'].help_text, 
            'Se for a primeira aula lançada (ordem = 1) esta será a data de início do curso também.',
        )
    
    def test_created_at_field(self):
        self.assertEqual(self.fields['created_at'].verbose_name, 'Criado em')
        self.assertTrue(self.fields['created_at'].auto_now_add)
        self.assertFalse(self.fields['created_at'].editable)
    
    def test_updated_at_field(self):
        self.assertEqual(self.fields['updated_at'].verbose_name, 'Atualizado em')
        self.assertTrue(self.fields['updated_at'].auto_now)
        self.assertFalse(self.fields['updated_at'].editable)
    
    def test_meta_class(self):
        self.assertEqual(self.lesson._meta.verbose_name, 'aula')
        self.assertEqual(self.lesson._meta.verbose_name_plural, 'aulas')
        self.assertTupleEqual(self.lesson._meta.ordering, ('order',))
    
    def test_object_name(self):
        self.assertEqual(str(self.lesson), 'Aula de Teste')
    
    def test_get_absolute_url_is_correct(self):
        expected = '/cursos/1/curso-de-teste/aulas/1/'
        self.assertURLEqual(self.lesson.get_absolute_url(), expected)
    
    def test_lesson_is_available(self):
        # Create lessons.
        present_date = date.today()
        past_date = present_date + timedelta(days=-1)
        future_date = present_date + timedelta(days=1)
        lesson1 = baker.make('courses.Lesson', release_date=present_date)
        lesson2 = baker.make('courses.Lesson', release_date=past_date)
        lesson3 = baker.make('courses.Lesson', release_date=future_date)
        
        # Available lessons has release_date <= today.
        self.assertTrue(lesson1.is_available())
        self.assertTrue(lesson2.is_available())

        # Unvailable lesson has release_date > today.
        self.assertFalse(lesson3.is_available())


class MaterialModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        course = baker.make('courses.Course', name='Curso de Teste', slug='curso-de-teste')
        lesson = baker.make('courses.Lesson', course=course)
        cls.material = baker.make('courses.Material', lesson=lesson, name='Material de Teste')
        cls.fields = {field.name: field for field in cls.material._meta.get_fields()}
    
    def test_lesson_field(self):
        self.assertEqual(self.fields['lesson'].verbose_name, 'Aula')

    def test_url_field(self):
        self.assertEqual(self.fields['url'].verbose_name, 'Vídeo da aula')
        self.assertTrue(self.fields['url'].blank)
        self.assertEqual(
            self.fields['url'].help_text, 
            'URL do vídeo. Por exemplo: https://www.youtube.com/embed/Mp0vhMDI7fA',
        )
    
    def test_resource_field(self):
        self.assertEqual(self.fields['resource'].verbose_name, 'Recurso')
        self.assertEqual(
            self.fields['resource'].upload_to(self.material, 'teste.txt'),
            'courses/lessons/materials/curso_de_teste/teste.txt',
        )
        self.assertEqual(
            self.fields['resource'].help_text,
            'Recurso usado na aula, como código base, anotações, imagem... Pode ser também o vídeo da aula.'
        )
    
    def test_meta_class(self):
        self.assertEqual(self.material._meta.verbose_name, 'material')
        self.assertEqual(self.material._meta.verbose_name_plural, 'materiais')
    
    def test_object_name(self):
        self.assertEqual(str(self.material), 'Material de Teste')
    
    def test_get_absolute_url_is_correct(self):
        expected = '/cursos/1/curso-de-teste/aulas/materiais/1/'
        self.assertURLEqual(self.material.get_absolute_url(), expected)
    
    def test_material_is_embedded(self):
        # Create materials.
        material1 = baker.make('courses.Material', url='https://www.youtube.com/embed/Mp0vhMDI7fA')
        material2 = baker.make('courses.Material')

        # Test if a course has an embedded video, that means has a url.
        self.assertTrue(material1.is_embedded())
        self.assertFalse(material2.is_embedded())


class EnrollmentModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.enrollment = baker.make('courses.Enrollment')
        cls.fields = {field.name: field for field in cls.enrollment._meta.get_fields()}
    
    def test_user_field(self):
        self.assertEqual(self.fields['user'].verbose_name, 'Usuário')
    
    def test_course_field(self):
        self.assertEqual(self.fields['course'].verbose_name, 'Curso')
    
    def test_status_field(self):
        self.assertEqual(self.fields['status'].verbose_name, 'Situação')
        self.assertListEqual(
            self.fields['status'].choices,
            [(0, 'Pendente'), (1, 'Aprovado'), (2, 'Cancelado')],
        )
        self.assertEqual(self.fields['status'].default, 0)
        self.assertTrue(self.fields['status'].blank)
    
    def test_created_at_field(self):
        self.assertEqual(self.fields['created_at'].verbose_name, 'Criado em')
        self.assertTrue(self.fields['created_at'].auto_now_add)
        self.assertFalse(self.fields['created_at'].editable)
    
    def test_updated_at_field(self):
        self.assertEqual(self.fields['updated_at'].verbose_name, 'Atualizado em')
        self.assertTrue(self.fields['updated_at'].auto_now)
        self.assertFalse(self.fields['updated_at'].editable)
    
    def test_meta_class(self):
        self.assertEqual(self.enrollment._meta.verbose_name, 'inscrição')
        self.assertEqual(self.enrollment._meta.verbose_name_plural, 'inscrições')
    
    def test_approve_enrollment(self):
        enrollment = baker.make('courses.Enrollment')
        
        # Change the status to approved (status = 1).
        self.assertEqual(enrollment.status, 0)
        enrollment.approve()
        self.assertEqual(enrollment.status, 1)
    
    def test_enrollment_is_approved(self):
        # Create an enrollment already approved.
        enrollment = baker.make('courses.Enrollment', status=1)
        self.assertTrue(enrollment.is_approved())


class AnnouncementModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        course = baker.make('courses.Course', slug='curso-de-teste')
        cls.announcement = baker.make('courses.Announcement', course=course, title='Anúncio de Teste')
        cls.fields = {field.name: field for field in cls.announcement._meta.get_fields()}
    
    def test_course_field(self):
        self.assertEqual(self.fields['course'].verbose_name, 'Curso')
    
    def test_title_field(self):
        self.assertEqual(self.fields['title'].verbose_name, 'Título')
        self.assertEqual(self.fields['title'].max_length, 100)
    
    def test_content_field(self):
        self.assertEqual(self.fields['content'].verbose_name, 'Conteúdo')
    
    def test_created_at_field(self):
        self.assertEqual(self.fields['created_at'].verbose_name, 'Criado em')
        self.assertTrue(self.fields['created_at'].auto_now_add)
        self.assertFalse(self.fields['created_at'].editable)
    
    def test_updated_at_field(self):
        self.assertEqual(self.fields['updated_at'].verbose_name, 'Atualizado em')
        self.assertTrue(self.fields['updated_at'].auto_now)
        self.assertFalse(self.fields['updated_at'].editable)
    
    def test_meta_class(self):
        self.assertEqual(self.announcement._meta.verbose_name, 'anúncio')
        self.assertEqual(self.announcement._meta.verbose_name_plural, 'anúncios')
        self.assertTupleEqual(self.announcement._meta.ordering, ('-created_at',))
    
    def test_object_name(self):
        self.assertEqual(str(self.announcement), 'Anúncio de Teste')
    
    def test_get_absolute_url_is_correct(self):
        expected = '/cursos/1/curso-de-teste/anuncios/1/'
        self.assertURLEqual(self.announcement.get_absolute_url(), expected)


class CommentModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        course = baker.make('courses.Course', slug='curso-de-teste')
        announcement = baker.make('courses.Announcement', course=course)
        cls.comment = baker.make('courses.Comment', announcement=announcement, content='Teste de comentário')
        cls.fields = {field.name: field for field in cls.comment._meta.get_fields()}
    
    def test_user_field(self):
        self.assertEqual(self.fields['user'].verbose_name, 'Usuário')
    
    def test_announcement_field(self):
        self.assertEqual(self.fields['announcement'].verbose_name, 'Anúncio')
    
    def test_content_field(self):
        self.assertEqual(self.fields['content'].verbose_name, 'Comentário')
    
    def test_created_at_field(self):
        self.assertEqual(self.fields['created_at'].verbose_name, 'Criado em')
        self.assertTrue(self.fields['created_at'].auto_now_add)
        self.assertFalse(self.fields['created_at'].editable)
    
    def test_updated_at_field(self):
        self.assertEqual(self.fields['updated_at'].verbose_name, 'Atualizado em')
        self.assertTrue(self.fields['updated_at'].auto_now)
        self.assertFalse(self.fields['updated_at'].editable)
    
    def test_meta_class(self):
        self.assertEqual(self.comment._meta.verbose_name, 'comentário')
        self.assertEqual(self.comment._meta.verbose_name_plural, 'comentários')
        self.assertTupleEqual(self.comment._meta.ordering, ('created_at',))
    
    def test_object_name(self):
        self.assertEqual(str(self.comment), 'Teste de comentário')
    
    def test_get_absolute_url_is_correct(self):
        expected = '/cursos/1/curso-de-teste/anuncios/1/editar-comentario/1/'
        self.assertURLEqual(self.comment.get_absolute_url(), expected)