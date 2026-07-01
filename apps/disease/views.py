from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import CropScan
from .serializers import CropScanSerializer

class CropScanViewSet(viewsets.ModelViewSet):
    serializer_class   = CropScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CropScan.objects.filter(submitted_by=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        scan = serializer.save(submitted_by=self.request.user, status='pending')
        # process synchronously — no celery needed, same pattern as forum AI
        try:
            from .vision import analyse_crop_image
            result = analyse_crop_image(scan.cloudinary_url)
            scan.disease_detected = result['disease_detected']
            scan.confidence_score = result['confidence_score']
            scan.treatment_advice = result['treatment_advice']
            scan.organic_alt      = result.get('organic_alt', '')
            scan.status           = result['status']
            scan.save()
        except Exception as e:
            print(f'scan processing failed: {e}')
            # still try celery as backup
            try:
                from .tasks import process_crop_scan
                process_crop_scan.delay(scan.id)
            except Exception:
                pass
