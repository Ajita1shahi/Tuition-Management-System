from datetime import date

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.apps import apps
from django.utils.crypto import get_random_string

from .models import CustomUser, PasswordResetRequest
from student.models import Student
from teacher.models import Teacher


def signup_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        role = request.POST.get("role")

        
        phone = request.POST.get("phone", "").strip() 
        if not phone:
            phone = "0000000000"  

        if not email or not password or not role:
            messages.error(request, "Please fill all required fields.")
            return redirect("signup")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect("signup")

    
        user = CustomUser.objects.create_user(
            username=email,   
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

      
        if role == "student":
            user.is_student = True
            user.user_type = "student"
            user.save()

            Student.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                student_id=f"S{user.id:03d}",
                gender="Others",
                date_of_birth=date.today(),
                student_class="Not Assigned",
                religion="N/A",
                joining_date=date.today(),
                mobile_number=phone,
            )

        elif role == "teacher":
            user.is_teacher = True
            user.user_type = "teacher"
            user.save()

           
            Teacher.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                teacher_id=f"T{user.id:03d}",
                gender="Others",
                qualification="Not Assigned",
                experience=0,
                joining_date=date.today(),
                mobile_number=phone,
                email=email,
            )

        elif role == "receptionist":
            user.is_receptionist = True
            user.user_type = "receptionist"
            user.save()

            
            Receptionist = apps.get_model("receptionist", "Receptionist")

           
            Receptionist.objects.create(
                user=user,
                phone=phone,
                address="",
                note_access=True,
            )

        elif role == "admin":
            user.is_admin = True
            user.user_type = "admin"
            user.is_staff = True
            user.is_superuser = True
            user.save()

        else:
            messages.error(request, "Invalid role selected.")
            user.delete()
            return redirect("signup")

        login(request, user)
        messages.success(request, "Signup successful!")
        return redirect("home")

    return render(request, "authentication/register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")

            # Redirect user based on role
            if user.user_type == "admin" or user.is_admin:
                return redirect("admin_dashboard")
            elif user.user_type == "teacher" or user.is_teacher:
                return redirect("teacher_dashboard")
            elif user.user_type == "student" or user.is_student:
                return redirect("student_dashboard")
            elif user.user_type == "receptionist" or user.is_receptionist:
                return redirect("receptionist_dashboard")

            messages.error(request, "Invalid user role. Please contact admin.")
            logout(request)
            return redirect("home")

        messages.error(request, "Invalid credentials")

    return render(request, "authentication/login.html")


def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        user = CustomUser.objects.filter(email=email).first()

        if user:
            token = get_random_string(32)
            reset_request = PasswordResetRequest.objects.create(user=user, email=email, token=token)
            reset_request.send_reset_email()
            messages.success(request, "Reset link sent to your email.")
        else:
            messages.error(request, "Email not found.")

    return render(request, "authentication/forgot-password.html")


def reset_password_view(request, token):
    reset_request = PasswordResetRequest.objects.filter(token=token).first()

    if not reset_request or not reset_request.is_valid():
        messages.error(request, "Invalid or expired reset link")
        return redirect("home")

    if request.method == "POST":
        new_password = request.POST.get("new_password", "")
        if not new_password:
            messages.error(request, "Password cannot be empty.")
            return redirect("reset_password", token=token)

        reset_request.user.set_password(new_password)
        reset_request.user.save()
        messages.success(request, "Password reset successful")
        return redirect("login")

    return render(request, "authentication/reset_password.html", {"token": token})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")
