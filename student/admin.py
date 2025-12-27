from django.contrib import admin
from .models import Student, Parent, StudentNote


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('father_name', 'mother_name', 'father_mobile', 'mother_mobile')
    search_fields = ('father_name', 'mother_name', 'father_mobile', 'mother_mobile')
    list_filter = ('father_name', 'mother_name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'student_id',
        'date_of_birth',
        'student_class',
        'joining_date',
        'mobile_number',
    )

    search_fields = ('first_name', 'last_name', 'student_id', 'student_class')
    list_filter = ('gender', 'student_class')

    readonly_fields = ('student_image',)

    # 👇 fields shown on the form (we ADD user here)
    fields = (
        'first_name',
        'last_name',
        'student_id',
        'student_class',
        'mobile_number',
        'teacher',
        'user',            # <— NEW: link to account
        'student_image',
    )


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ("student", "title", "created_by", "created_at", "is_private")
    search_fields = ("student__first_name", "title", "created_by__username")
    list_filter = ("is_private", "created_at")
