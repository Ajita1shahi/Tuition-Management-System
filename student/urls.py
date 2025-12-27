from django.contrib import admin
from django.urls import path, include
from .import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('add/', views.add_student, name='add_student'),
    path('student/<str:slug>/', views.view_student, name='view_student'),
    path('edit/<str:slug>/', views.edit_student, name='edit_student'),
    path('delete/<str:slug>/', views.delete_student, name='delete_student'),
    path('my-fees/', views.student_my_fees, name='student_my_fees'),
    path('learning-activities/', views.student_learning_activities, name='student_learning_activities'),
    path('performance/', views.student_performance, name='student_performance'),
    path('subjects/', views.student_subjects, name='student_subjects'),
    path('tests/', views.student_tests, name='student_tests'),
    path('tests/passed/', views.student_tests_passed, name='student_tests_passed'),
    path('courses/', views.all_courses, name='all_courses'),
    path("assign-teacher/<int:student_id>/", views.assign_teacher, name="assign_teacher"),
    path("plan/read/<int:plan_id>/", views.mark_plan_read, name="mark_plan_read"),


]
