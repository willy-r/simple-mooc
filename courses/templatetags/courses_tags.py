from django import template

from courses.models import Enrollment

register = template.Library()


@register.simple_tag
def load_courses(user):
    """Loads the courses of a user.
    
    Usage: {% load_courses user as var %}{{ var }}
    """
    return Enrollment.objects.filter(user=user)