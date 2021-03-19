from django import template

from courses.models import Enrollment

register = template.Library()


@register.simple_tag
def load_enrollments(user):
    """Loads the enrollments of a user.
    
    Usage: {% load_enrollments user as var %}{{ var }}
    """
    return Enrollment.objects.filter(user=user)