from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Receptionist

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_receptionist_profile(sender, instance, created, **kwargs):
    if created and instance.user_type == "receptionist":
        Receptionist.objects.create(
            user=instance,
            full_name=instance.first_name + " " + instance.last_name
        )
