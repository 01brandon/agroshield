from celery import shared_task
from .models import CropScan

@shared_task
def process_crop_scan(scan_id):
    # called automatically when a new scan is created
    try:
        scan = CropScan.objects.get(id=scan_id)

        from .vision import analyse_crop_image
        result = analyse_crop_image(scan.cloudinary_url)

        scan.disease_detected = result['disease_detected']
        scan.confidence_score = result['confidence_score']
        scan.treatment_advice = result['treatment_advice']
        scan.organic_alt      = result['organic_alt']
        scan.status           = result['status']
        scan.save()

        return f'scan {scan_id} processed - {result["disease_detected"]}'

    except CropScan.DoesNotExist:
        return f'scan {scan_id} not found'
    except Exception as e:
        return f'scan {scan_id} failed: {str(e)}'
