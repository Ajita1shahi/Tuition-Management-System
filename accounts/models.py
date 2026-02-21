from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from teacher.models import Teacher
from student.models import Student


class Fee(models.Model):
    STATUS_CHOICES = [
        ("Paid", "Paid"),
        ("Pending", "Pending"),
    ]

    MONTH_CHOICES = [
        ("January", "January"),
        ("February", "February"),
        ("March", "March"),
        ("April", "April"),
        ("May", "May"),
        ("June", "June"),
        ("July", "July"),
        ("August", "August"),
        ("September", "September"),
        ("October", "October"),
        ("November", "November"),
        ("December", "December"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.CharField(max_length=20, choices=MONTH_CHOICES, default="January")

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    remaining = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
    )
    date_paid = models.DateField(auto_now_add=True)

    def clean(self):
        errors = {}

        if self.total_amount is None or self.total_amount < 0:
            errors["total_amount"] = "Total amount must be zero or positive."

        if self.amount_paid is None or self.amount_paid < 0:
            errors["amount_paid"] = "Amount paid must be zero or positive."

        if (
            self.total_amount is not None
            and self.amount_paid is not None
            and self.amount_paid > self.total_amount
        ):
            errors["amount_paid"] = "Amount paid cannot be greater than total amount."

        if self.date_paid and self.date_paid > timezone.localdate():
            errors["date_paid"] = "Payment date cannot be in the future."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        
        if self.total_amount is not None and self.amount_paid is not None:
            self.remaining = self.total_amount - self.amount_paid
            if self.remaining <= 0:
                self.remaining = 0
                self.status = "Paid"
            else:
                self.status = "Pending"

        
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.month} ({self.status})"


class Expense(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)

    def clean(self):
        errors = {}

        if self.amount is None or self.amount <= 0:
            errors["amount"] = "Expense amount must be greater than zero."

        if self.date and self.date > timezone.localdate():
            errors["date"] = "Expense date cannot be in the future."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.amount}"


class Salary(models.Model):
    STATUS_CHOICES = (
        ("Paid", "Paid"),
        ("Pending", "Pending"),
    )

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    date_paid = models.DateField(auto_now_add=True)

    def clean(self):
        errors = {}

        if self.amount is None or self.amount <= 0:
            errors["amount"] = "Salary amount must be greater than zero."

        if self.date_paid and self.date_paid > timezone.localdate():
            errors["date_paid"] = "Salary payment date cannot be in the future."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher} - {self.month} - {self.amount}"
