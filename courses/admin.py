from django.contrib import admin

from .models import (
    Course, Enrollment, Announcement, Comment, Lesson, Material
)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'start_date', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class MaterialInline(admin.StackedInline):
    model = Material


class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'order', 'release_date')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    inlines = (MaterialInline,)


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register([Enrollment, Announcement, Comment])