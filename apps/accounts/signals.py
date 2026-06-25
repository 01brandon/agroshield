from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def send_welcome_on_register(sender, instance, created, **kwargs):
    # sends a welcome email when a new user registers
    if created:
        try:
            from config.email import send_welcome_email
            send_welcome_email(instance)
        except Exception as e:
            print(f'welcome email failed for {instance.email}: {e}')
