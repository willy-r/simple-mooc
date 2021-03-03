from django.contrib import messages
from django.shortcuts import render, get_object_or_404

from .models import Course
from .forms import ContactCourseForm


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