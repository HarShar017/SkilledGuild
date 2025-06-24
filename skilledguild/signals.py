from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserDashboard

@receiver(post_save, sender=User)
def create_user_dashboard(sender, instance, created, **kwargs):
    if created:
        UserDashboard.objects.create(user=instance)
