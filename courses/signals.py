from core.mail import send_mail_template


def post_save_announcement(sender, instance, created, **kwargs):
    """Sends an e-mail when an announcement is created.

    Sends an e-mail for each of the users with an enrollment on the
    course when an announcement of that course is created.
    """
    # Only send e-mail if a new object was created.
    if created:
        subject = f'[{instance.course}] {instance.title}'
        context = {'announcement': instance}
        enrollments = instance.course.enrollments.filter(
            course=instance.course, status=1,
        )
        # This open a new connection each time that send an e-mail to an user.
        for enrollment in enrollments:
            recipient_list = [enrollment.user.email]
            send_mail_template(
                subject, 
                'courses/announcement_email.html', 
                context, 
                recipient_list,
            )