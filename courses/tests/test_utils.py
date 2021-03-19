from django.test import TestCase

from model_bakery import baker

from courses.utils import material_directory_path


def create_material(course_name):
    course = baker.make('courses.Course', name=course_name)
    lesson = baker.make('courses.Lesson', course=course)
    return baker.make('courses.Material', lesson=lesson)


class MaterialDirectoryPathTests(TestCase):

    def test_material_directory_whitespace(self):
        instance = create_material('Curso de Teste')
        filename = 'teste.txt'
        material_path = material_directory_path(instance, filename)
        self.assertEqual(material_path, 'courses/lessons/materials/curso_de_teste/teste.txt')
    
    def test_material_directory_no_whitespace(self):
        instance = create_material('Teste')
        filename = 'teste.txt'
        material_path = material_directory_path(instance, filename)
        self.assertEqual(material_path, 'courses/lessons/materials/teste/teste.txt')