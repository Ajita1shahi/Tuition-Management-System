from django.urls import path
from . import views

urlpatterns = [
    # Admin-side receptionist management
    path('', views.receptionist_list, name='receptionist_list'),
    path('add/', views.add_receptionist, name='add_receptionist'),
    path('<int:pk>/', views.view_receptionist, name='view_receptionist'),

    # Receptionist dashboard
    path('dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),

    # Student + notes pages
    path('students/', views.receptionist_students, name='receptionist_students'),
    path('notes/<slug:slug>/', views.receptionist_notes, name='receptionist_notes'),
    path('notes/<slug:slug>/add/', views.add_note, name='receptionist_add_note'),
]
