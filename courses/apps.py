from django.apps import AppConfig
from django.db.models.signals import post_save


from .signals import post_save_announcement


class CoursesConfig(AppConfig):
    name = 'courses'

    def ready(self):
        Announcement = self.get_model('Announcement')

        post_save.connect(
            post_save_announcement, 
            sender=Announcement, 
            dispatch_uid='post_save_announcement',
        )