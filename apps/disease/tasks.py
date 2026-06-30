from celery import shared_task
from .models import CropScan

@shared_task
def process_crop_scan(scan_id):
    try:
        scan = CropScan.objects.get(id=scan_id)
        from .vision import analyse_crop_image
        r = analyse_crop_image(scan.cloudinary_url)
        scan.disease_detected = r['disease_detected']
        scan.confidence_score = r['confidence_score']
        scan.treatment_advice = r['treatment_advice']
        scan.organic_alt = r['organic_alt']
        scan.status = r['status']
        scan.save()
    except CropScan.DoesNotExist:
        pass
