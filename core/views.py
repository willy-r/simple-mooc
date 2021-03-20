from django.shortcuts import render
from django.contrib.auth import get_user_model

from courses.models import Course


def home(request):
    """The homepage."""
    return render(request, 'home.html')


def contact(request):
    """Contact page."""
    return render(request, 'contact.html')


# TODO 
# def about(request):
#     """About page."""
#     courses = Course.objects.all()
    
#     User = get_user_model()
#     students = User.objects.exclude(groups__name='instructor').exclude(is_staff=True)
#     instructors = User.objects.filter(groups__name='instructor')

#     context = {
#         'courses': courses,
#         'students': students,
#         'instructors': instructors,
#     }
#     return render(request, 'about.html', context)