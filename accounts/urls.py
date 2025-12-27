from django.urls import path
from . import views

urlpatterns = [
    path('', views.accounts_dashboard, name='accounts_dashboard'),
    path('fees/', views.fee_list, name='fee_list'),
    path('add-fee/', views.add_fee, name='add_fee'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('salary/', views.salary_list, name='salary_list'),
    path('add-salary/', views.add_salary, name='add_salary'),
]
