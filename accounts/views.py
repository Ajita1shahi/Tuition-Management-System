from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages

from student.models import Student
from .models import Fee, Expense, Salary
from .forms import FeeForm, ExpenseForm, SalaryForm




@login_required
def accounts_dashboard(request):
    total_fees = Fee.objects.aggregate(total=Sum("amount_paid"))["total"] or 0
    total_expenses = Expense.objects.aggregate(total=Sum("amount"))["total"] or 0
    total_salary = Salary.objects.aggregate(total=Sum("amount"))["total"] or 0

    net_balance = total_fees - (total_expenses + total_salary)

    context = {
        "total_fees": total_fees,
        "total_expenses": total_expenses,
        "total_salary": total_salary,
        "net_balance": net_balance,
        "recent_fees": Fee.objects.order_by("-date_paid")[:5],
        "recent_expenses": Expense.objects.order_by("-date")[:5],
        "recent_salaries": Salary.objects.order_by("-date_paid")[:5],
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def fee_list(request):
    user = request.user

    if getattr(user, "user_type", "") == "student":
        try:
            student = Student.objects.get(user=user)
            fees = Fee.objects.filter(student=student)
        except Student.DoesNotExist:
            fees = Fee.objects.none()
    else:
        fees = Fee.objects.all().select_related("student")

    return render(request, "accounts/fees_list.html", {"fees": fees})


@login_required
def add_fee(request):
    if request.method == "POST":
        form = FeeForm(request.POST)
        if form.is_valid():
            try:
                fee = form.save() 
                messages.success(request, "Fee record added successfully.")
                return redirect("fee_list")
            except Exception as e:
                messages.error(request, f"Error saving fee: {e}")
    else:
        form = FeeForm()

    return render(request, "accounts/add_fee.html", {"form": form})


@login_required
def expense_list(request):
    expenses = Expense.objects.order_by("-date")
    return render(request, "accounts/expenses_list.html", {"expenses": expenses})


@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Expense added successfully.")
                return redirect("expense_list")
            except Exception as e:
                messages.error(request, f"Error saving expense: {e}")
    else:
        form = ExpenseForm()

    return render(request, "accounts/add_expense.html", {"form": form})


@login_required
def salary_list(request):
    salaries = Salary.objects.order_by("-date_paid").select_related("teacher")
    return render(request, "accounts/salary_list.html", {"salaries": salaries})


@login_required
def add_salary(request):
    if request.method == "POST":
        form = SalaryForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Salary record added successfully.")
                return redirect("salary_list")
            except Exception as e:
                messages.error(request, f"Error saving salary: {e}")
    else:
        form = SalaryForm()

    return render(request, "accounts/add_salary.html", {"form": form})
