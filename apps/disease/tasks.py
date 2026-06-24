from celery import shared_task
from .models import CropScan

@shared_task
def process_crop_scan(scan_id):
    # called after a scan is submitted - runs ai diagnosis
    try:
        scan = CropScan.objects.get(id=scan_id)

        # placeholder logic - replace with real google cloud vision call
        # when google credentials are configured
        scan.disease_detected = 'awaiting ai diagnosis'
        scan.confidence_score = 0.0
        scan.treatment_advice = 'please wait while our ai analyses your crop image'
        scan.status           = 'pending'
        scan.save()

        return f'scan {scan_id} queued for processing'
    except CropScan.DoesNotExist:
        return f'scan {scan_id} not found'
