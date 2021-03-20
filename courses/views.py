from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import ContactCourseForm, CommentForm
from .models import Course, Enrollment, Lesson, Material
from .decorators import enrollment_required


def index(request):
    """Displays the courses available on the platform."""
    courses = Course.objects.all()

    context = {'courses': courses}
    return render(request, 'courses/index.html', context)


def details(request, pk, slug):
    """Displays the details about a course."""
    course = get_object_or_404(Course, pk=pk, slug=slug)

    form = ContactCourseForm(request.POST or None)
    if form.is_valid():
        form.send_mail(course)
        messages.success(request, 'Seu e-mail foi enviado com sucesso!')
        return redirect(course)

    context = {
        'course': course,
        'form': form,
    }
    return render(request, 'courses/details.html', context)


@login_required
def make_enrollment(request, pk, slug):
    """Makes the enrollment on a course.
    
    For default all courses in the platform is free and any users can
    make a enrollment at any time.
    """
    course = get_object_or_404(Course, pk=pk, slug=slug)
    # Gets the enrollment or create.
    # If create, then for default approve the enrollment.
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, 
        course=course,
    )
    if created:
        enrollment.approve()
        messages.success(request, f'Você foi inscrito no curso "{course}" com sucesso!')
    else:
        messages.info(request, f'Você já está inscrito no curso "{course}".')
    return redirect('accounts:dashboard')


@login_required
@enrollment_required
def undo_enrollment(request, pk, slug):
    """Undos a enrollment from a course."""
    course = request.course

    if request.method == 'POST':
        enrollment = get_object_or_404(course.enrollments, user=request.user, course=course)
        enrollment.delete()
        messages.success(request, 'Sua inscrição foi cancelada com sucesso!')
        return redirect('accounts:dashboard')
    
    context = {'course': course}
    return render(request, 'courses/undo_enrollment.html', context)


@login_required
@enrollment_required
def announcements(request, pk, slug):
    """Displays the announcements of a course."""
    course = request.course
    
    context = {
        'course': course,
        'announcements': course.announcements.all(),
    }
    return render(request, 'courses/announcements.html', context)


@login_required
@enrollment_required
def announcement_details(request, pk, slug, announcement_pk):
    """Displays the details about an announcement and the comments."""
    course = request.course
    announcement = get_object_or_404(course.announcements.all(), pk=announcement_pk)

    # Creates a comment on the announcement.
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.save(request.user, announcement)
        messages.success(request, 'Seu comentário foi enviado.')
        return redirect(announcement)

    context = {
        'course': course,
        'announcement': announcement,
        'comments': announcement.comments.all(),
        'form': form,
    }
    return render(request, 'courses/announcement_details.html', context)


@login_required
@enrollment_required
def edit_comment(request, pk, slug, announcement_pk, comment_pk):
    """Edits a comment on the announcement details page."""
    course = request.course
    announcement = get_object_or_404(course.announcements.all(), pk=announcement_pk)
    comment = get_object_or_404(announcement.comments.all(), pk=comment_pk, user=request.user)

    # Edits the comment.
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save(request.user, announcement)
        messages.success(request, 'Seu comentário foi editado com sucesso.')
        return redirect(announcement)

    context = {
        'course': course,
        'announcement': announcement,
        'comment': comment,
        'form': form,
    }
    return render(request, 'courses/edit_comment.html', context)


@login_required
@enrollment_required
def lessons(request, pk, slug):
    """Displays the lessons of a course."""
    course = request.course
    lessons = course.released_lessons()

    if request.user.is_staff:
        lessons = course.lessons.all()

    context = {
        'course': course,
        'lessons': lessons,
    }
    return render(request, 'courses/lessons.html', context)


@login_required
@enrollment_required
def lesson_details(request, pk, slug, lesson_pk):
    """Displays the details about a lesson."""
    course = request.course
    lesson = get_object_or_404(Lesson, course=course, pk=lesson_pk)

    if not request.user.is_staff and not lesson.is_available():
        messages.error(request, 'Esta aula não está disponível.')
        return redirect('courses:lessons', pk=course.pk, slug=course.slug)
    
    # This just work if the instructor set the lesson order correctly.
    try:
        prev_lesson = course.released_lessons().get(order=lesson.order - 1)
    except lesson.DoesNotExist:
        prev_lesson = None
    
    try:
        next_lesson = course.released_lessons().get(order=lesson.order + 1)
    except lesson.DoesNotExist:
        next_lesson = None

    context = {
        'course': course,
        'lesson': lesson,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
    }
    return render(request, 'courses/lesson_details.html', context)


@login_required
@enrollment_required
def material_details(request, pk, slug, material_pk):
    """Displays the embedded video of a lesson."""
    course = request.course
    material = get_object_or_404(Material, lesson__course=course, pk=material_pk)
    lesson = material.lesson

    if not request.user.is_staff and not lesson.is_available():
        messages.error(request, 'Este material não está disponível.')
        return redirect('courses:lessons', pk=course.pk, slug=course.slug)
    
    if not material.is_embedded():
        messages.error(request, 'Esta aula não possui um vídeo disponível, tente um dos recursos abaixo.')
        return redirect(lesson)
    
    context = {
        'course': course,
        'lesson': lesson,
        'material': material,
    }
    return render(request, 'courses/material_details.html', context)