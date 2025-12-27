from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_list, name='teacher_list'),
    path('add/', views.add_teacher, name='add_teacher'),
    path('teacher/<str:slug>/', views.view_teacher, name='view_teacher'),
    path('edit/<str:slug>/', views.edit_teacher, name='edit_teacher'),
    path('delete/<str:slug>/', views.delete_teacher, name='delete_teacher'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path("my-subjects/", views.teacher_subjects, name="teacher_subjects"),
    path('add-subject/', views.add_subject, name='add_subject'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('tests/add/', views.add_test, name='add_test'),
    path('marks/add/', views.add_marks, name='add_marks'),
    path('students/', views.teacher_students, name='teacher_students'),
    path('my-subjects/', views.teacher_subjects, name='teacher_subjects'),
    path('improvement-plan/<int:student_id>/', views.give_improvement_plan, name='give_improvement_plan'),
    path('improvement-plans/', views.teacher_improvement_plans, name='teacher_improvement_plans'),

]  
