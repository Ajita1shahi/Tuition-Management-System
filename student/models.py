from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Parent(models.Model):
    father_name = models.CharField(max_length=100)
    father_occupation = models.CharField(max_length=100)
    father_mobile = models.CharField(max_length=100)
    father_email = models.EmailField(max_length=100)
    mother_name = models.CharField(max_length=100)
    mother_occupation = models.CharField(max_length=100)
    mother_mobile = models.CharField(max_length=100)
    mother_email = models.EmailField(max_length=100)
    present_address = models.TextField()
    permanent_address = models.TextField()

    def __str__(self):
        return f"{self.father_name} & {self.mother_name}"


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=100, unique=True)

    gender = models.CharField(
        max_length=10,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other'),
        ]
    )

    date_of_birth = models.DateField(null=True, blank=True)
    student_class = models.CharField(max_length=100)
    religion = models.CharField(max_length=50)
    joining_date = models.DateField(null=True, blank=True)
    mobile_number = models.CharField(max_length=10)

    student_image = models.ImageField(
        upload_to='student_images/',
        null=True,
        blank=True
    )

    parent = models.OneToOneField(
        Parent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    teacher = models.ForeignKey(
        'teacher.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_students'
    )

    def clean(self):
        """
        Model-level validation for Student.
        Ensures sensible dates and basic consistency.
        """
        super().clean()

        today = timezone.now().date()

        if self.date_of_birth and self.date_of_birth > today:
            raise ValidationError({
                "date_of_birth": "Date of birth cannot be in the future."
            })

       
        if self.joining_date and self.joining_date > today:
            raise ValidationError({
                "joining_date": "Joining date cannot be in the future."
            })

        if self.date_of_birth and self.joining_date:
            if self.joining_date <= self.date_of_birth:
                raise ValidationError({
                    "joining_date": "Joining date must be after the student's date of birth."
                })

        
        if self.date_of_birth:
            age_years = (today.year - self.date_of_birth.year) - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
            if age_years < 3:
                raise ValidationError({
                    "date_of_birth": "Student age must be at least 3 years."
                })

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.first_name}-{self.last_name}-{self.student_id}")
            slug = base_slug
            counter = 1
            while Student.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"


class StudentNote(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="notes"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=120)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.student} - {self.title}"


class Marks(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="marks"
    )
    subject = models.CharField(max_length=100)
    score = models.FloatField()
    date_recorded = models.DateField(auto_now_add=True)

    def clean(self):
        
        super().clean()
        if self.score < 0 or self.score > 100:
            raise ValidationError({
                "score": "Marks/score must be between 0 and 100."
            })

    def percentage(self, total_marks=100):
        return (self.score / total_marks) * 100

    def __str__(self):
        return f"{self.student} - {self.subject}: {self.score}"