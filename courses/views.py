from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import ContactCourseForm
from .models import Course, Enrollment


def index(request):
    """Displays the courses."""
    courses = Course.objects.all()

    context = {'courses': courses}
    return render(request, 'courses/index.html', context)


def details(request, pk, slug):
    """Displays the details about a course."""
    course = get_object_or_404(Course, pk=pk, slug=slug)

    # Process the form on that page.
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
        messages.info(request, f'Você já está inscrito no curso {course.name}.')

    return redirect('accounts:dashboard')


@login_required
def undo_enrollment(request, pk, slug):
    """Undos a enrollment from a course of a user."""
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
    
    context = {'course': course}
    return render(request, 'courses/announcements.html', context)