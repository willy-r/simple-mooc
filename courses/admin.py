from django.contrib import admin

from .models import (
    Course, Enrollment, Announcement, Comment, Lesson, Material
)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'total_lessons', 'total_enrollments', 'start_date_view', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    exclude = ('start_date',)

    def total_lessons(self, obj):
        """Returns the quantity of lessons released that the course has."""
        return obj.released_lessons().count()
    total_lessons.short_description = 'Aulas'

    def total_enrollments(self, obj):
        """Returns the quantity of enrollments approved that the course has."""
        return obj.enrollments.filter(status=1).count()
    total_enrollments.short_description = 'Inscrições'

    def start_date_view(self, obj):
        return obj.start_date
    start_date_view.empty_value_display = 'Sem data'
    start_date_view.short_description = 'Data de início'


class MaterialInline(admin.StackedInline):
    model = Material


class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'order', 'is_available', 'release_date')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'course')
    list_editable = ('order', 'release_date')
    list_select_related = ('course',)
    inlines = (MaterialInline,)

    def save_model(self, request, obj, form, change):
        # Define the start_date of a course with the release_date from
        # the first lesson created. 
        if obj.order == 1:
            obj.course.start_date = obj.release_date
            obj.course.save()
        super().save_model(request, obj, form, change)


class CommentInline(admin.TabularInline):
    model = Comment
    min_num = 2


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'total_comments', 'created_at')
    search_fields = ('title',)
    list_filter = ('created_at', 'course')
    inlines = (CommentInline,)

    def total_comments(self, obj):
        """Returns the total of comments that the announcemente has."""
        return obj.comments.all().count()
    total_comments.short_description = 'Comentários'


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'status', 'created_at')
    search_fields = ('course', 'user')
    list_filter = ('course', 'user')


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)