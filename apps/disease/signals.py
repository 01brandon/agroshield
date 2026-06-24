from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CropScan

@receiver(post_save, sender=CropScan)
def trigger_scan_processing(sender, instance, created, **kwargs):
    # when a new scan is saved, queue it for ai processing
    if created:
        from .tasks import process_crop_scan
        process_crop_scan.delay(instance.id)
