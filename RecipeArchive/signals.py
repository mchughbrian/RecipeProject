from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .management.commands.assign_starter_recipes import assign_starter_recipes
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)  # Changed to get_or_create


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=User)
def create_starter_recipes(sender, instance, created, **kwargs):
    if created:
        assign_starter_recipes(instance)