from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from .models import Course, Enrollment


def enrollment_required(view_func):
    """A decorator for verify if a user has a enrollment on a course.
    
    Must have a 'pk' and a 'slug' parameters on the view_func to work.
    """
    def _wrapper(request, *args, **kwargs):
        pk, slug = kwargs['pk'], kwargs['slug']
        course = get_object_or_404(Course, pk=pk, slug=slug)
        has_permission = request.user.is_staff
        
        if not has_permission:
            try:
                enrollment = Enrollment.objects.get(
                    user=request.user,
                    course=course,
                )
            except Enrollment.DoesNotExist:
                message = 'Desculpe, mas você não tem permissão para acessar esta página.'
            else:
                if enrollment.is_approved():
                    has_permission = True
                else:
                    message = 'A sua inscrição no curso ainda está pendente.'
        
        if not has_permission:
            messages.error(request, message)
            return redirect('accounts:dashboard')
        
        request.course = course
        return view_func(request, *args, **kwargs)
    return _wrapper