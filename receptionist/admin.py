from django.contrib import admin
from .models import Receptionist, ReceptionistNote

@admin.register(Receptionist)
class ReceptionistAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'started_on', 'user')
    search_fields = ('full_name', 'user__username')

@admin.register(ReceptionistNote)
class ReceptionistNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'receptionist', 'created_at')
    search_fields = ('title', 'receptionist__full_name')
