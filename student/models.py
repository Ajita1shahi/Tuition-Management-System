from django.db import models
from django.utils.text import slugify
from django.conf import settings

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
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=100, unique=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    date_of_birth = models.DateField(null=True, blank=True)
    student_class = models.CharField(max_length=100)
    religion = models.CharField(max_length=50)
    joining_date = models.DateField(null=True, blank=True)
    mobile_number = models.CharField(max_length=10)
    student_image = models.ImageField(upload_to='student_images/', null=True, blank=True)
    parent = models.OneToOneField(Parent, on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    

    teacher = models.ForeignKey(
        'teacher.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_students'
    )
    
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
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="notes")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=120)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.student} - {self.title}"

class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="marks")
    subject = models.CharField(max_length=100)
    score = models.FloatField()
    date_recorded = models.DateField(auto_now_add=True)

    def percentage(self, total_marks=100):
        return (self.score / total_marks) * 100

    def __str__(self):
        return f"{self.student} - {self.subject}: {self.score}"

