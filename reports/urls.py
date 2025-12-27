from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.student_report, name='student_report'),
    path('fees/', views.fee_report, name='fee_report'),

]
