from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TraceabilityBatch

@receiver(post_save, sender=TraceabilityBatch)
def generate_batch_qr(sender, instance, created, **kwargs):
    # generates a qr code automatically when a batch is first created
    if created and not instance.qr_code:
        try:
            from .qr import generate_qr_code
            _, url              = generate_qr_code(instance.id, instance.listing_id)
            instance.qr_code    = url
            instance.save(update_fields=['qr_code'])
        except Exception as e:
            print(f'qr generation failed for batch {instance.id}: {e}')
