from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import ContactCourseForm, CommentForm
from .models import Course, Enrollment


def index(request):
    """Displays the courses available on the platform."""
    courses = Course.objects.all()

    context = {'courses': courses}
    return render(request, 'courses/index.html', context)


def details(request, pk, slug):
    """Displays the details about a course."""
    course = get_object_or_404(Course, pk=pk, slug=slug)

    # Processes the form on that page.
    if request.method != 'POST':
        form = ContactCourseForm()
    else:
        form = ContactCourseForm(request.POST)
        if form.is_valid():
            form.send_mail(course)
            messages.success(request, 'Seu e-mail foi enviado com sucesso!')
            form = ContactCourseForm()

    context = {
        'course': course,
        'form': form,
    }
    return render(request, 'courses/details.html', context)


@login_required
def make_enrollment(request, pk, slug):
    """Makes the enrollment logic.
    
    For default all courses in the platform is free and any users can
    make a enrollment at any time.
    """
    course = get_object_or_404(Course, pk=pk, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, course=course
    )
    if created:
        enrollment.approve()
        messages.success(request, f'Você foi inscrito no curso "{course.name}" com sucesso!')
    else:
        messages.info(request, f'Você já está inscrito no curso "{course.name}".')

    return redirect('accounts:dashboard')


@login_required
def undo_enrollment(request, pk, slug):
    """Undos a enrollment from a course."""
    course = get_object_or_404(Course, pk=pk, slug=slug)
    # The user has access of this course?
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, 'Sua inscrição foi cancelada com sucesso!')
        return redirect('accounts:dashboard')
    
    context = {
        'enrollment': enrollment,
        'course': course,
    }
    return render(request, 'courses/undo_enrollment.html', context)


@login_required
def announcements(request, pk, slug):
    """Displays the announcements of a course."""
    course = get_object_or_404(Course, pk=pk, slug=slug)

    if not request.user.is_staff:
        # The user has access of this course?
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        # Is the user approved on the course?
        if not enrollment.is_approved():
            messages.error(request, 'A sua inscrição está pendente.')
            return redirect('accounts:dashboard')
    
    context = {
        'course': course,
        'announcements': course.announcements.all(),
    }
    return render(request, 'courses/announcements.html', context)


@login_required
def announcement_details(request, course_pk, slug, announcement_pk):
    """Displays the details about an announcement and the comments."""
    course = get_object_or_404(Course, pk=course_pk, slug=slug)

    if not request.user.is_staff:
        # The user has access of this course?
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        # Is the user approved on the course?
        if not enrollment.is_approved():
            messages.error(request, 'A sua inscrição está pendente.')
            return redirect('accounts:dashboard')
    
    announcement = get_object_or_404(course.announcements.all(), pk=announcement_pk)

    # Adds a comment on the announcement.
    if request.method != 'POST':
        form = CommentForm()
    else:
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save(request.user, announcement)
            messages.success(request, 'Seu comentário foi enviado.')
            form = CommentForm()

    context = {
        'course': course,
        'announcement': announcement,
        'comments': announcement.comments.all(),
        'form': form,
    }
    return render(request, 'courses/announcement_details.html', context)


@login_required
def edit_comment(request, course_pk, slug, announcement_pk, comment_pk):
    """Edits a comment on the announcement details page."""
    course = get_object_or_404(Course, pk=course_pk, slug=slug)
    # The user has access of this course?
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    if not enrollment.is_approved():
        messages.error(request, 'A sua inscrição está pendente.')
        return redirect('accounts:dashboard')

    announcement = get_object_or_404(course.announcements.all(), pk=announcement_pk)
    comment = get_object_or_404(announcement.comments.all(), pk=comment_pk, user=request.user)

    # Edits the comment.
    if request.method != 'POST':
        form = CommentForm(instance=comment)
    else:
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save(request.user, announcement)
            messages.success(request, 'Seu comentário foi editado com sucesso.')
            return redirect(
                'courses:announcement_details',
                course_pk=course.pk, 
                slug=course.slug, 
                announcement_pk=announcement.pk,
            )

    context = {
        'course': course,
        'announcement': announcement,
        'comment': comment,
        'form': form,
    }
    return render(request, 'courses/edit_comment.html', context)