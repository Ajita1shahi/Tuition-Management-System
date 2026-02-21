from django.contrib import admin
from django.urls import path, include
from .import views

urlpatterns = [
    path('', views.index, name='home'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/receptionist/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('add-receptionist/', views.add_receptionist, name='add_receptionist'),
    path('dashboard/receptionist/notes/', views.receptionist_notes, name='receptionist_notes'),
    path('dashboard/receptionist/students/', views.receptionist_students, name='receptionist_students'),
    path('notification/mark-as-read/', views.mark_notification_as_read, name='mark_notifications_as_read'),
    path('notification/clear-all/', views.clear_all_notification, name='clear_all_notifications'),
    path('', views.index, name='home'),

]
