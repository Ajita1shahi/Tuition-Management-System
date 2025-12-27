from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from teacher.models import Teacher, Subject, Marks, ImprovementPlan
from .models import Student, Parent
from tuition.models import Notification
from django.db.models import Avg
from accounts.models import Fee
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json


def create_notification(user, message):
    if user:
        Notification.objects.create(user=user, message=message)



def add_student(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, "A student with this ID already exists.")
            return redirect('add_student')

        parent = Parent.objects.create(
            father_name=request.POST.get('father_name'),
            father_occupation=request.POST.get('father_occupation'),
            father_mobile=request.POST.get('father_mobile'),
            father_email=request.POST.get('father_email'),
            mother_name=request.POST.get('mother_name'),
            mother_occupation=request.POST.get('mother_occupation'),
            mother_mobile=request.POST.get('mother_mobile'),
            mother_email=request.POST.get('mother_email'),
            present_address=request.POST.get('present_address'),
            permanent_address=request.POST.get('permanent_address')
        )

        student = Student.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            student_id=student_id,
            gender=request.POST.get('gender'),
            date_of_birth=request.POST.get('date_of_birth'),
            student_class=request.POST.get('student_class'),
            religion=request.POST.get('religion'),
            joining_date=request.POST.get('joining_date'),
            mobile_number=request.POST.get('mobile_number'),
            student_image=request.FILES.get('student_image'),
            parent=parent,
            user=None  
        )

        create_notification(request.user, f"New student {student.first_name} {student.last_name} added.")
        messages.success(request, "Student added successfully!")
        return redirect('student_list')

    return render(request, 'students/add-student.html')


def student_list(request):
    students = Student.objects.select_related('parent').all()
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(
        request,
        'students/students.html',
        {
            'student_list': students,
            'unread_notifications': unread_notifications
        }
    )


def edit_student(request, slug):
    student = get_object_or_404(Student, slug=slug)
    parent = student.parent

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        if Student.objects.filter(student_id=student_id).exclude(pk=student.pk).exists():
            messages.error(request, "A student with this ID already exists.")
            return redirect('edit_student', slug=slug)

        if parent:
            parent.father_name = request.POST.get('father_name')
            parent.father_occupation = request.POST.get('father_occupation')
            parent.father_mobile = request.POST.get('father_mobile')
            parent.father_email = request.POST.get('father_email')
            parent.mother_name = request.POST.get('mother_name')
            parent.mother_occupation = request.POST.get('mother_occupation')
            parent.mother_mobile = request.POST.get('mother_mobile')
            parent.mother_email = request.POST.get('mother_email')
            parent.present_address = request.POST.get('present_address')
            parent.permanent_address = request.POST.get('permanent_address')
            parent.save()

        student.first_name = request.POST.get('first_name')
        student.last_name = request.POST.get('last_name')
        student.student_id = student_id
        student.gender = request.POST.get('gender')
        student.date_of_birth = request.POST.get('date_of_birth')
        student.student_class = request.POST.get('student_class')
        student.religion = request.POST.get('religion')
        student.joining_date = request.POST.get('joining_date')
        student.mobile_number = request.POST.get('mobile_number')

        if request.FILES.get('student_image'):
            student.student_image = request.FILES.get('student_image')

        student.save()

        create_notification(request.user, f"Student {student.first_name} {student.last_name} updated.")
        messages.success(request, "Student updated successfully!")
        return redirect('student_list')

    return render(request, 'students/edit-student.html', {'student': student, 'parent': parent})


def view_student(request, slug):
    student = get_object_or_404(Student, slug=slug)
    return render(request, 'students/student-details.html', {'student': student})


def delete_student(request, slug):
    if request.method == 'POST':
        student = get_object_or_404(Student, slug=slug)
        student_name = f"{student.first_name} {student.last_name}"
        student.delete()
        create_notification(request.user, f"Student {student_name} has been deleted.")
        messages.success(request, "Student deleted successfully!")
        return redirect('student_list')
    return HttpResponseForbidden()


from django.db.models import Avg
from accounts.models import Fee
@login_required
def student_dashboard(request):
   
    student = get_object_or_404(Student, user=request.user)
    marks_qs = (
        Marks.objects
        .filter(student=student)
        .select_related("subject", "teacher")
        .order_by("-id")
    )

    total_tests = marks_qs.count()
    tests_passed = marks_qs.filter(marks_obtained__gte=40).count()

    subjects_enrolled = (
        Subject.objects
        .filter(subject_marks__student=student)
        .distinct()
        .count()
    )

    average_score = (
        round(marks_qs.aggregate(avg=Avg("marks_obtained"))["avg"] or 0, 2)
        if total_tests
        else 0
    )

    
    recent_tests = list(marks_qs[:5])


    chart_marks = list(marks_qs[:7])[::-1] 
    labels = [f"Test {i + 1}" for i, _ in enumerate(chart_marks)]
    scores = [m.marks_obtained for m in chart_marks]

    
    improvement_plans = (
        ImprovementPlan.objects
        .filter(student=student)
        .select_related("teacher", "teacher__user")
        .order_by("-created_at")
    )

   
    fee = (
        Fee.objects
        .filter(student=student)
        .order_by("-date_paid")
        .first()
    )

    context = {
        "student": student,
        "subjects_enrolled": subjects_enrolled,
        "total_tests": total_tests,
        "tests_passed": tests_passed,
        "average_score": average_score,
        "recent_tests": recent_tests,
        "labels_json": json.dumps(labels),
        "scores_json": json.dumps(scores),
        "improvement_plans": improvement_plans,
        "fee": fee,
        "unread_notifications": Notification.objects.filter(
            user=request.user, is_read=False
        ),
    }

    return render(request, "students/student-dashboard.html", context)


@login_required
def student_my_fees(request):
    student = get_object_or_404(Student, user=request.user)


    fees = Fee.objects.filter(student=student).order_by("date_paid")

    if fees.exists():
        total_fee = sum(f.total_amount for f in fees)
        total_paid = sum(f.amount_paid for f in fees)
        total_remaining = sum(f.remaining for f in fees)
    else:
        total_fee = 0
        total_paid = 0
        total_remaining = 0

    context = {
        "student": student,
        "fees": fees,
        "total_fee": total_fee,
        "total_paid": total_paid,
        "total_remaining": total_remaining,
    }
    return render(request, "students/my-fees.html", context)



@login_required
def student_learning_activities(request):
    student = Student.objects.get(user=request.user)
    marks = student.student_marks.select_related('subject', 'teacher').all()

    passed_count = marks.filter(marks_obtained__gte=40).count()

    context = {
        'marks': marks,
        'passed_count': passed_count,
    }
    return render(request, "students/learning-activities.html", context)

@login_required
def student_performance(request):
    """
    Detailed performance page:
    - Shows list of all tests (marks)
    - Shows improvement plans given by teachers
    """
    student = get_object_or_404(Student, user=request.user)

    marks = (
        Marks.objects
        .filter(student=student)
        .select_related("subject", "teacher")
        .order_by("-id")
    )

    improvement_plans = (
        ImprovementPlan.objects
        .filter(student=student)
        .select_related("teacher")
        .order_by("-created_at")
    )

    context = {
        "student": student,
        "marks": marks,
        "improvement_plans": improvement_plans,
    }
    return render(request, "students/performance.html", context)


@login_required
def student_subjects(request):
    student = Student.objects.get(user=request.user)
    subjects = Subject.objects.filter(subject_marks__student=student).distinct()
    context = {"student": student, "subjects": subjects}
    return render(request, "students/subjects.html", context)


@login_required
def student_tests(request):
    student = Student.objects.get(user=request.user)
    tests = student.student_marks.select_related('subject')
    context = {"student": student, "tests": tests}
    return render(request, "students/tests.html", context)


@login_required
def student_tests_passed(request):
    student = Student.objects.get(user=request.user)
    tests_passed = student.student_marks.filter(marks_obtained__gte=40).select_related('subject')
    context = {"student": student, "tests_passed": tests_passed}
    return render(request, "students/tests-passed.html", context)


@login_required
def all_courses(request):
    student = Student.objects.get(user=request.user)
    courses = []  
    context = {"student": student, "courses": courses}
    return render(request, "students/all-courses.html", context)


def assign_teacher(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    teachers = Teacher.objects.all()

    if request.method == "POST":
        teacher_id = request.POST.get("teacher")
        teacher = Teacher.objects.get(id=teacher_id)
        student.teacher = teacher
        student.save()
        return redirect("student_list")

    return render(
        request,
        "students/assign_teacher.html",
        {"student": student, "teachers": teachers},
    )


@require_POST
@login_required
def mark_plan_read(request, plan_id):
    plan = ImprovementPlan.objects.filter(id=plan_id, student__user=request.user).first()
    if plan:
        plan.is_read = True
        plan.save()
    return JsonResponse({"ok": True})
