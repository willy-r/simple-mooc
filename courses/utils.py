def material_directory_path(instance, filename):
    """Returns the material directory.

    The materials for a lesson will be saved in a directory with the
    name of the course.
    """
    course_name = instance.lesson.course.name.replace(' ', '_').lower()
    return f'courses/lessons/materials/{course_name}/{filename}'