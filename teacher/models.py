from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from student.models import Student
from django.conf  import settings


class Teacher(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others'),
    ]
     
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,related_name='teacher_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    teacher_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    qualification = models.CharField(max_length=150)
    experience = models.PositiveIntegerField(default=0)
    joining_date = models.DateField(null=True, blank=True)
    mobile_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    teacher_image = models.ImageField(upload_to='teacher_images/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.first_name}-{self.last_name}-{self.teacher_id}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('view_teacher', kwargs={'slug': self.slug})



class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return self.subject_name

class Test(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="tests"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="tests"
    )
    name = models.CharField(max_length=200)
    total_marks = models.FloatField(default=100)
    test_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject.subject_name} - {self.name}"



class Marks(models.Model):
    student = models.ForeignKey('student.Student', on_delete=models.CASCADE, related_name='student_marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_marks')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_marks')
    marks_obtained = models.FloatField()
    total_marks = models.FloatField(default=100)

    def percentage(self):
        return (self.marks_obtained / self.total_marks) * 100

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.marks_obtained})"

class Receptionist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True) 
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    joined_date = models.DateField(auto_now_add=True)
    note_access = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

class ImprovementPlan(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="improvement_plans"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="improvement_plans"
    )

    title = models.CharField(max_length=200)
    instructions = models.TextField()
    weak_topics = models.CharField(max_length=255, blank=True)

    question_paper_image = models.ImageField(
        upload_to="improvement_plans/question_papers/",
        null=True,
        blank=True
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.title}"
