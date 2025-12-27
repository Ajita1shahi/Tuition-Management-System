from django.db import models
from django.conf import settings
from student.models import Student


class Receptionist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="receptionist_profile"
    )
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    started_on = models.DateField(auto_now_add=True)

    note_access = models.BooleanField(default=True)  # ✅ ADD THIS

    def __str__(self):
        return self.full_name or self.user.username


class ReceptionistNote(models.Model):
    receptionist = models.ForeignKey(
        Receptionist,
        on_delete=models.CASCADE,
        related_name="notes"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="reception_notes",
        null=True,  
        blank=True  
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        name = self.receptionist.full_name or self.receptionist.user.username
        return f"{self.title} - {name}"
