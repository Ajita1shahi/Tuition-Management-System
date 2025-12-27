from django.db import models
from django.conf import settings
from teacher.models import Teacher
from student.models import Student

class Fee(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    ]

    MONTH_CHOICES = [
        ('January', 'January'), 
        ('February', 'February'), 
        ('March', 'March'), 
        ('April', 'April'), 
        ('May', 'May'), 
        ('June', 'June'), 
        ('July', 'July'), 
        ('August', 'August'), 
        ('September', 'September'), 
        ('October', 'October'), 
        ('November', 'November'), 
        ('December', 'December'),
    ]
 

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.CharField(max_length=20, choices=MONTH_CHOICES, default='January')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    remaining = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    date_paid = models.DateField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.student} - {self.month} ({self.status})"
    
class Expense(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"

class Salary(models.Model):
    teacher = models.ForeignKey('teacher.Teacher', on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=(('Paid', 'Paid'), ('Pending', 'Pending')))
    date_paid = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher} - {self.month} - {self.amount}"
