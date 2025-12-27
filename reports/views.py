from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from teacher.models import Subject, Marks
from student.models import Student
from accounts.models import Fee  
from django.db.models import F, ExpressionWrapper, DecimalField

def student_report(request):
    students = Student.objects.all()

    total_students = students.count()

    
    high_performers = students.filter(student_marks__marks_obtained__gte=80).count()
    average_students = students.filter(student_marks__marks_obtained__gte=50, student_marks__marks_obtained__lt=80).count()
    low_performers = students.filter(student_marks__marks_obtained__lt=50).count()

   
    subjects = Subject.objects.annotate(avg_marks=Avg('subject_marks__marks_obtained'))

    subject_names = [s.subject_name for s in subjects]   # change to your actual field
    subject_avgs = [round(s.avg_marks or 0, 2) for s in subjects]

    context = {
        'students': students,
        'total_students': total_students,
        'high_performers': high_performers,
        'average_students': average_students,
        'low_performers': low_performers,
        'subject_names': subject_names,
        'subject_avgs': subject_avgs,
    }
    return render(request, 'reports/student_report.html', context)


  

def fee_report(request):
    fees = Fee.objects.annotate(
        amount_due=ExpressionWrapper(F('total_amount') - F('amount_paid'), output_field=DecimalField())
    )

    total_collected = fees.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_due = fees.aggregate(Sum('remaining'))['remaining__sum'] or 0
    total_students = fees.values('student').distinct().count()

    paid_count = fees.filter(status='Paid').count()
    pending_count = fees.filter(status='Pending').count()
    partially_paid = fees.filter(status='Partially Paid').count()

    context = {
        'fees': fees,
        'total_collected': total_collected,
        'total_due': total_due,
        'total_students': total_students,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'partially_paid': partially_paid,
    }
    return render(request, 'reports/fee_report.html', context)