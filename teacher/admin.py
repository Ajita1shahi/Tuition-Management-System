from django.contrib import admin
from .models import Teacher, Subject, Marks , Receptionist


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'teacher_id', 'qualification', 'experience')
    search_fields = ('first_name', 'last_name', 'teacher_id')
    list_filter = ('gender'),


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    
    list_display = ('subject_name', 'teacher')
    search_fields = ('subject_name',)
    list_filter = ('teacher',)


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    
    list_display = ('student', 'subject', 'marks_obtained', 'teacher')
    search_fields = ('student__first_name', 'subject__subject_name')
    list_filter = ('subject', 'teacher')
    ordering = ('-marks_obtained',)


@admin.register(Receptionist)
class ReceptionistAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "joined_date", "note_access")
    search_fields = ("user__username", "user__email", "phone")