from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
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


subscription_created = Signal(["user", "subscription_id"])


@receiver(subscription_created, sender=Profile)
def handle_subscription_created(sender, user_profile, subscription_id, **kwargs):
    user_profile.stripe_subscription_id = subscription_id
    user_profile.has_subscription = True
    user_profile.save()

    # Send a confirmation email
    '''send_mail(
        subject='Subscription Successful',
        message='Thank you for subscribing! Your subscription has been activated.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )'''