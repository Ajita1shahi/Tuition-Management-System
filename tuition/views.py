from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from teacher.models import Teacher
from student.models import Student
from accounts.models import Fee, Expense, Salary
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from .models import Notification
from django.contrib import messages
from django.http import JsonResponse
from receptionist.models import Receptionist

def index(request):
    return render(request, "authentication/login.html")

def dashboard(request):
    unread_notification = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    unread_notification_count = unread_notification.count()

    context = {
        'unread_notification': unread_notification,
        'unread_notification_count': unread_notification_count,
    }
    return render(request,"students/student-dashboard.html",context)

def mark_notification_as_read(request):
    if request.method == 'POST':
        notification = Notification.objects.filter(user=request.user, is_read=False)
        notification.update(is_read=True)
        return JsonResponse({'status': 'success'})
    return HttpResponseForbidden()

def clear_all_notification(request):
    if request.method == 'POST':
        notification = Notification.objects.filter(user=request.user)
        notification.delete()
        return JsonResponse({'status': 'success'})
    return HttpResponseForbidden()

User = get_user_model()

from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib.auth import get_user_model

from teacher.models import Teacher
from student.models import Student
from receptionist.models import Receptionist
from accounts.models import Fee, Expense, Salary
from tuition.models import Notification

User = get_user_model()


def admin_dashboard(request):

    if not request.user.is_authenticated or request.user.user_type != "admin":
        return redirect("login")
    
    # Notifications
    unread_notification = Notification.objects.filter(
        user=request.user, is_read=False
    ).order_by('-created_at')
    unread_notification_count = unread_notification.count()

    # Core counts
    total_teachers = Teacher.objects.count()
    total_students = Student.objects.count()

    # 🔹 FIXED: match the receptionist LIST (Receptionist model), not users
    total_receptionists = Receptionist.objects.count()

    # Financial aggregates
    total_fees = Fee.objects.aggregate(total=Sum("amount_paid"))["total"] or 0
    total_expenses = Expense.objects.aggregate(total=Sum("amount"))["total"] or 0
    total_salary = Salary.objects.aggregate(total=Sum("amount"))["total"] or 0

    net_balance = total_fees - (total_expenses + total_salary)
    if net_balance < 0:
        balance_color = "bg-gradient-danger"
    else:
        balance_color = "bg-gradient-success"

    # Recent records
    recent_fees = Fee.objects.order_by("-date_paid")[:5]
    recent_expenses = Expense.objects.order_by("-date")[:5]
    recent_salaries = Salary.objects.order_by("-date_paid")[:5]

    context = {
        "user_type": request.user.user_type,
        "total_teachers": total_teachers,
        "total_students": total_students,
        "total_receptionists": total_receptionists,
        "total_fees": total_fees,
        "total_expenses": total_expenses,
        "total_salary": total_salary,
        "net_balance": net_balance,
        "balance_color": balance_color,
        "recent_fees": recent_fees,
        "recent_expenses": recent_expenses,
        "recent_salaries": recent_salaries,
        "unread_notification": unread_notification,
        "unread_notification_count": unread_notification_count,
    }

    return render(request, "dashboard/admin_dashboard.html", context)


def teacher_dashboard(request):
    return render(request, 'dashboard/teacher_dashboard.html', {'user_type': request.user.user_type})

def student_dashboard(request):
   return render(request, 'dashboard/student_dashboard.html', {'user_type': request.user.user_type})

def receptionist_dashboard(request):
    return render(request, 'dashboard/receptionist_dashboard.html', {'user_type': request.user.user_type})

def receptionist_notes(request):
    return render(request, 'receptionists/receptionist_notes.html', {'user_type': request.user.user_type})

def receptionist_students(request):
    return render(request, 'receptionists/receptionist_students.html', {'user_type': request.user.user_type})

def add_receptionist(request):
    if not request.user.is_authenticated or request.user.user_type != "admin":
        return redirect("login")

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("add_receptionist")

        new_user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            user_type="receptionist"
        )
        messages.success(request, "Receptionist added successfully!")
        return redirect("admin_dashboard")

    return render(request, "receptionists/add_receptionist.html")


