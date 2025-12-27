from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

from student.models import Student
from accounts.models import Fee
from .models import Receptionist, ReceptionistNote

User = get_user_model()


def _is_receptionist(user):
    return user.is_authenticated and getattr(user, "user_type", "") == "receptionist"


@login_required
def receptionist_dashboard(request):
    if not _is_receptionist(request.user):
        return HttpResponseForbidden("Receptionist access only.")

    total_students = Student.objects.count()
    latest_students = Student.objects.order_by("-id")[:5]
    pending_fees = Fee.objects.filter(status="pending").count()
    total_notes = ReceptionistNote.objects.filter(
        receptionist__user=request.user
    ).count()

    context = {
        "total_students": total_students,
        "latest_students": latest_students,
        "pending_fees": pending_fees,
        "total_notes": total_notes,
        "user_type": request.user.user_type,
    }
    return render(request, "dashboard/receptionist_dashboard.html", context)


@login_required
def receptionist_students(request):
    if not _is_receptionist(request.user):
        return HttpResponseForbidden("Receptionist access only.")

    students = Student.objects.all().order_by("first_name")

    return render(request, "receptionists/receptionist_students.html", {
        "students": students,
        "user_type": request.user.user_type,
    })



@login_required
def receptionist_notes(request, slug):
    if not _is_receptionist(request.user):
        return HttpResponseForbidden("Receptionist access only.")

   
    receptionist = Receptionist.objects.filter(user=request.user).first()
    if not receptionist:
        return HttpResponseForbidden("Receptionist profile missing for this user.")

    student = get_object_or_404(Student, slug=slug)
    
    notes = ReceptionistNote.objects.filter(
        receptionist=receptionist,
        student=student
    )

    return render(request, "receptionists/receptionist_notes.html", {
        "student": student,
        "notes": notes,
        "user_type": request.user.user_type
    })



@login_required
def add_note(request, slug):
    if not _is_receptionist(request.user):
        return HttpResponseForbidden("Receptionist access only.")

    student = get_object_or_404(Student, slug=slug)

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        ReceptionistNote.objects.create(
            receptionist=request.user.receptionist_profile,
            student=student,
            title=title,
            content=content,
        )

        messages.success(request, "Note added successfully!")
        return redirect("receptionist_notes", slug=slug)

    return render(request, "receptionists/receptionist_add_note.html", {
        "student": student,
        "user_type": request.user.user_type,
    })


@login_required
def receptionist_list(request):
    receptionists = Receptionist.objects.all()
    return render(request, "receptionists/receptionist_list.html", {
        "receptionists": receptionists
    })


@login_required
def add_receptionist(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("add_receptionist")

        user = User.objects.create_user(
            username=username,
            email=email,
            user_type="receptionist",
            is_receptionist=True,
        )
        Receptionist.objects.create(
            user=user,
            full_name=username,
            phone=phone
        )

        messages.success(request, "Receptionist added successfully!")
        return redirect("receptionist_list")

    return render(request, "receptionists/add_receptionist.html")


@login_required
def view_receptionist(request, pk):
    receptionist = get_object_or_404(Receptionist, pk=pk)
    return render(request, "receptionists/receptionist_details.html", {
        "receptionist": receptionist
    })
