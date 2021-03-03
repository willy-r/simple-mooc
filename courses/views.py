from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import ContactCourseForm
from .models import Course, Enrollment


def index(request):
    """Display the courses."""
    courses = Course.objects.all()

    context = {'courses': courses}
    return render(request, 'courses/index.html', context)


def details(request, pk, slug):
    """Display the details about a course."""
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
    """Make the enrollment logic.
    
    For default all courses in the platform is free and any users can
    make a enrollment at any time.
    """
    course = get_object_or_404(Course, pk=pk, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, course=course
    )
    if created:
        enrollment.approve()
    return redirect('accounts:dashboard')