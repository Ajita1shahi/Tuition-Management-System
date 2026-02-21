from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.db.models import Avg, F
from django.utils import timezone

from .models import Teacher, Subject, Marks, ImprovementPlan, Test
from student.models import Student
from datetime import datetime, date

User = get_user_model()


def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'teachers/teachers.html', {'teacher_list': teachers})


def add_teacher(request):
    if request.method == 'POST':
        teacher_id = (request.POST.get('teacher_id') or "").strip()
        email = (request.POST.get('email') or "").strip()
        first_name = (request.POST.get('first_name') or "").strip()
        last_name = (request.POST.get('last_name') or "").strip()
        gender = request.POST.get('gender') or ""
        qualification = (request.POST.get('qualification') or "").strip()
        experience_raw = (request.POST.get('experience') or "").strip()
        mobile_number = (request.POST.get('mobile_number') or "").strip()

      
        if not teacher_id or not email or not first_name or not last_name:
            messages.error(request, "Teacher ID, email, first name, and last name are required.")
            return redirect('add_teacher')

        
        if Teacher.objects.filter(teacher_id=teacher_id).exists():
            messages.error(request, "Teacher ID already exists.")
            return redirect('add_teacher')

       
        if User.objects.filter(username=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('add_teacher')

        try:
            experience = int(experience_raw or 0)
            if experience < 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Experience must be a non-negative whole number.")
            return redirect('add_teacher')

        if not mobile_number.isdigit() or len(mobile_number) < 7:
            messages.error(request, "Please enter a valid mobile number.")
            return redirect('add_teacher')

       
        user = User.objects.create_user(
            username=email,
            email=email,
            password=teacher_id  
        )
        user.user_type = "teacher"
        user.is_teacher = True
        user.save()

        Teacher.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            teacher_id=teacher_id,
            gender=gender,
            qualification=qualification,
            experience=experience,
            mobile_number=mobile_number,
            email=email,
        )

        messages.success(request, "Teacher added successfully.")
        return redirect('teacher_list')

    return render(request, 'teachers/add-teacher.html')


def view_teacher(request, slug):
    teacher = get_object_or_404(Teacher, slug=slug)

    total_students = Student.objects.filter(teacher=teacher).distinct().count()
    total_classes = Subject.objects.filter(teacher=teacher).count()
    total_subjects = total_classes
    marks_qs = Marks.objects.filter(teacher=teacher)

    avg_val = marks_qs.aggregate(avg=Avg("marks_obtained"))["avg"] or 0
    average_marks = round(avg_val, 2)

    context = {
        "teacher": teacher,
        "total_students": total_students,
        "total_classes": total_classes,
        "total_subjects": total_subjects,
        "average_marks": average_marks,
    }
    return render(request, "teachers/teacher-details.html", context)


def edit_teacher(request, slug):
    teacher = get_object_or_404(Teacher, slug=slug)

    if request.method == 'POST':
        teacher.first_name = (request.POST.get('first_name') or "").strip()
        teacher.last_name = (request.POST.get('last_name') or "").strip()
        teacher.gender = request.POST.get('gender') or teacher.gender
        teacher.qualification = (request.POST.get('qualification') or "").strip()

        exp_raw = (request.POST.get('experience') or "").strip()
        try:
            teacher.experience = int(exp_raw or 0)
            if teacher.experience < 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Experience must be a non-negative whole number.")
            return redirect('edit_teacher', slug=slug)

        mobile_number = (request.POST.get('mobile_number') or "").strip()
        if not mobile_number.isdigit() or len(mobile_number) < 7:
            messages.error(request, "Please enter a valid mobile number.")
            return redirect('edit_teacher', slug=slug)

        email = (request.POST.get('email') or "").strip()
       
        if email and User.objects.filter(username=email).exclude(pk=teacher.user_id).exists():
            messages.error(request, "Another user with this email already exists.")
            return redirect('edit_teacher', slug=slug)

        teacher.mobile_number = mobile_number
        teacher.email = email
        teacher.save()

       
        if teacher.user:
            teacher.user.email = email
            teacher.user.username = email
            teacher.user.save()

        messages.success(request, "Teacher updated.")
        return redirect('teacher_list')

    return render(request, 'teachers/edit-teacher.html', {'teacher': teacher})


def delete_teacher(request, slug):
    teacher = get_object_or_404(Teacher, slug=slug)
    teacher.delete()
    messages.success(request, "Teacher deleted.")
    return redirect('teacher_list')


@login_required
def teacher_dashboard(request):
    teacher = Teacher.objects.filter(user=request.user).first()

    if teacher:
        teacher_marks = Marks.objects.filter(teacher=teacher)
        total_students = Student.objects.filter(teacher=teacher).distinct().count()
        total_classes = Subject.objects.filter(teacher=teacher).count()
        tests_qs = Test.objects.filter(teacher=teacher)
    else:
        teacher_marks = Marks.objects.all()
        total_students = Student.objects.count()
        total_classes = Subject.objects.count()
        tests_qs = Test.objects.all()

    # ✅ Now count actual Test records
    total_tests = tests_qs.count()

    average_marks = teacher_marks.aggregate(avg=Avg('marks_obtained'))['avg'] or 0

    high_performers = teacher_marks.filter(marks_obtained__gte=80).count()
    average_performers = teacher_marks.filter(
        marks_obtained__gte=50, marks_obtained__lt=80
    ).count()
    low_performers = teacher_marks.filter(marks_obtained__lt=50).count()

    if teacher:
        subject_qs = Subject.objects.filter(teacher=teacher)
    else:
        subject_qs = Subject.objects.all()

    subject_wise = subject_qs.annotate(
        avg_score=Avg('subject_marks__marks_obtained')
    )

    subject_names = [s.subject_name for s in subject_wise]
    subject_averages = [(s.avg_score or 0) for s in subject_wise]

    high_students = list(
        teacher_marks.filter(marks_obtained__gte=80)
        .annotate(
            student_pk=F('student__pk'),
            name=F('student__first_name'),
            marks=F('marks_obtained'),
        )
        .values('student_pk', 'name', 'marks')
    )

    average_students = list(
        teacher_marks.filter(marks_obtained__gte=50, marks_obtained__lt=80)
        .annotate(
            student_pk=F('student__pk'),
            name=F('student__first_name'),
            marks=F('marks_obtained'),
        )
        .values('student_pk', 'name', 'marks')
    )

    low_students = list(
        teacher_marks.filter(marks_obtained__lt=50)
        .annotate(
            student_pk=F('student__pk'),
            name=F('student__first_name'),
            marks=F('marks_obtained'),
        )
        .values('student_pk', 'name', 'marks')
    )

    context = {
        "teacher": teacher,
        "total_students": total_students,
        "total_classes": total_classes,
        "total_tests": total_tests,  
        "average_marks": round(average_marks, 2),

        "high_performers": high_performers,
        "average_performers": average_performers,
        "low_performers": low_performers,

        "subject_names": subject_names,
        "subject_averages": subject_averages,

        "high_students": high_students,
        "average_students": average_students,
        "low_students": low_students,

        "upcoming_classes": [],
        "notices": [],
    }

    return render(request, "teachers/teacher-dashboard.html", context)


@login_required
def add_subject(request):
    teacher = get_object_or_404(Teacher, user=request.user)

    if request.method == "POST":
        subject_name = (request.POST.get("subject_name") or "").strip()
        code = (request.POST.get("code") or "").strip()
        description = (request.POST.get("description") or "").strip()

        if not subject_name or not code:
            messages.error(request, "Please enter both Subject Name and Code.")
        elif Subject.objects.filter(code=code).exists():
            messages.error(request, "A subject with this code already exists.")
        else:
            Subject.objects.create(
                teacher=teacher,
                subject_name=subject_name,
                code=code,
                description=description,
            )
            messages.success(request, "Subject added successfully.")
            return redirect("teacher_subjects")

    return render(request, "teachers/add-subject.html", {"teacher": teacher})


@login_required
def subject_list(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    subjects = Subject.objects.filter(teacher=teacher)
    return render(request, 'teachers/subjects.html', {'subjects': subjects})


@login_required
def add_test(request):
    teacher = Teacher.objects.filter(user=request.user).first()
    if not teacher:
        messages.error(request, "No teacher profile linked to this user.")
        return redirect("teacher_dashboard")

    subjects = Subject.objects.filter(teacher=teacher)

    if request.method == "POST":
        subject_id = request.POST.get("subject")
        test_name = (request.POST.get("test_name") or "").strip()
        total_marks_raw = (request.POST.get("total_marks") or "100").strip()
        test_date_str = (request.POST.get("test_date") or "").strip()

        if not (subject_id and test_name):
            messages.error(request, "Please select a subject and enter a test name.")
        else:
            try:
                subject = Subject.objects.get(id=subject_id, teacher=teacher)
            except Subject.DoesNotExist:
                messages.error(request, "Invalid subject selection.")
                return redirect("add_test")

            
            try:
                total_marks = float(total_marks_raw)
                if total_marks <= 0:
                    raise ValueError
            except ValueError:
                messages.error(request, "Total marks must be a positive number.")
                return redirect("add_test")

            test_obj = Test(
                teacher=teacher,
                subject=subject,
                name=test_name,
                total_marks=total_marks,
            )

            if test_date_str:
                try:
                    parsed_date = datetime.strptime(test_date_str, "%Y-%m-%d").date()
                    if parsed_date > date.today():
                        messages.error(request, "Test date cannot be in the future.")
                        return redirect("add_test")
                    test_obj.test_date = parsed_date
                except ValueError:
                    messages.error(request, "Invalid test date format.")
                    return redirect("add_test")

            test_obj.save()
            messages.success(request, "Test created successfully.")
            return redirect("teacher_dashboard")

    return render(request, "teachers/add-test.html", {
        "subjects": subjects,
    })


@login_required
def add_marks(request):
    teacher = Teacher.objects.filter(user=request.user).first()

    if teacher:
        subjects = Subject.objects.filter(teacher=teacher)
        students = Student.objects.filter(teacher=teacher).distinct()
    else:
        subjects = Subject.objects.all()
        students = Student.objects.all()

    if request.method == "POST":
        student_id = request.POST.get("student") or request.POST.get("student_id")
        subject_id = request.POST.get("subject") or request.POST.get("subject_id")
        marks_raw = (
            request.POST.get("marks_obtained")
            or request.POST.get("score")
            or request.POST.get("marks")
        )
        total_marks_raw = (request.POST.get("total_marks") or "100").strip()

        if not (student_id and subject_id and marks_raw):
            messages.error(request, "Please select a student, a subject and enter marks.")
        else:
            try:
                student = Student.objects.get(id=student_id)
                subject = Subject.objects.get(id=subject_id)
            except (Student.DoesNotExist, Subject.DoesNotExist):
                messages.error(request, "Invalid student or subject selection.")
                return redirect("add_marks")

           
            try:
                total_marks = float(total_marks_raw)
                if total_marks <= 0:
                    raise ValueError
            except ValueError:
                messages.error(request, "Total marks must be a positive number.")
                return redirect("add_marks")

            try:
                marks_value = float(marks_raw)
                if marks_value < 0 or marks_value > total_marks:
                    messages.error(
                        request,
                        f"Marks must be between 0 and {total_marks}."
                    )
                    return redirect("add_marks")
            except ValueError:
                messages.error(request, "Please enter a valid numeric value for marks.")
                return redirect("add_marks")

            Marks.objects.create(
                teacher=teacher,
                student=student,
                subject=subject,
                marks_obtained=marks_value,
                total_marks=total_marks,
            )
            messages.success(request, "Marks added successfully.")
            return redirect("teacher_dashboard")

    return render(request, "teachers/add-marks.html", {
        "subjects": subjects,
        "students": students,
    })


@login_required
def teacher_students(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    students = Student.objects.filter(teacher=teacher)
    return render(request, "teachers/teacher-students.html", {"students": students})


@login_required
def teacher_subjects(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    subjects = Subject.objects.filter(teacher=teacher)
    context = {"teacher": teacher, "subjects": subjects}
    return render(request, "teachers/teacher-subjects.html", context)


@login_required
def give_improvement_plan(request, student_id):
    teacher = get_object_or_404(Teacher, user=request.user)
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        instructions = (request.POST.get("instructions") or "").strip()
        weak_topics = (request.POST.get("weak_topics") or "").strip()
        question_paper_image = request.FILES.get("question_paper_image")

        if not title or not instructions:
            messages.error(request, "Title and instructions are required.")
            return redirect("give_improvement_plan", student_id=student.id)

        ImprovementPlan.objects.create(
            teacher=teacher,
            student=student,
            title=title,
            instructions=instructions,
            weak_topics=weak_topics,
            question_paper_image=question_paper_image,
        )
        messages.success(request, "Improvement plan created.")
        return redirect("teacher_dashboard")

    return render(request, "teachers/give-improvement-plan.html", {"student": student})


@login_required
def teacher_improvement_plans(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    plans = ImprovementPlan.objects.filter(teacher=teacher)
    return render(request, "teachers/teacher-improvement-plans.html", {"plans": plans})


@login_required
def improvement_plan_report(request):
    """Report page for improvement plans (teacher side)."""
    teacher = get_object_or_404(Teacher, user=request.user)

    plans = ImprovementPlan.objects.filter(teacher=teacher).select_related("student")

    student_id = request.GET.get("student")
    status = request.GET.get("status")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if student_id:
        plans = plans.filter(student_id=student_id)

    if status == "new":
        plans = plans.filter(is_read=False)
    elif status == "read":
        plans = plans.filter(is_read=True)

    def parse_date(value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return None

    df = parse_date(date_from)
    dt = parse_date(date_to)

    if df:
        plans = plans.filter(created_at__date__gte=df)
    if dt:
        plans = plans.filter(created_at__date__lte=dt)

    
    if df and dt and df > dt:
        messages.error(request, "Start date cannot be later than end date.")

    total_plans = plans.count()
    unread_count = plans.filter(is_read=False).count()
    distinct_students = plans.values("student_id").distinct().count()

    students_for_filter = Student.objects.filter(teacher=teacher).order_by("first_name", "last_name")

    context = {
        "teacher": teacher,
        "plans": plans.order_by("-created_at"),
        "total_plans": total_plans,
        "unread_count": unread_count,
        "distinct_students": distinct_students,

        "students_for_filter": students_for_filter,
        "selected_student": student_id or "",
        "selected_status": status or "all",
        "selected_date_from": date_from or "",
        "selected_date_to": date_to or "",
    }
    return render(request, "teachers/improvement-plan-report.html", context)
