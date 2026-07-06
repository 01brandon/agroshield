from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from .models import CropScan
from .serializers import CropScanSerializer

@extend_schema_view(
    list=extend_schema(
        tags=['disease'],
        summary='List all crop scans submitted by the authenticated user',
        description='Returns scans ordered by most recent. Each scan includes disease name, confidence score, treatment advice, and organic alternative.'
    ),
    create=extend_schema(
        tags=['disease'],
        summary='Submit a crop image for AI diagnosis',
        description='Upload a Cloudinary image URL. The image is analysed immediately using Google Gemini 1.5 Flash vision AI. Results are returned in the same response.',
        examples=[
            OpenApiExample('Example Request', value={
                'farm': 1,
                'cloudinary_url': 'https://res.cloudinary.com/dfk5falaw/image/upload/v1/agroshield/scans/sample.jpg',
                'notes': 'Yellowing on lower leaves, brown spots visible on stem'
            }, request_only=True),
            OpenApiExample('Example Response', value={
                'id': 5,
                'disease_detected': 'Maize Dwarf Mosaic Virus (MDMV)',
                'confidence_score': 0.87,
                'status': 'confirmed',
                'treatment_advice': 'Remove and destroy infected plants. Apply imidacloprid to control aphid vectors.',
                'organic_alt': 'Introduce natural predators. Apply neem oil spray weekly.',
                'created_at': '2026-07-03T09:15:00Z'
            }, response_only=True)
        ]
    ),
    retrieve=extend_schema(tags=['disease'], summary='Retrieve a specific crop scan result'),
    destroy=extend_schema(tags=['disease'], summary='Delete a crop scan record'),
)
class CropScanViewSet(viewsets.ModelViewSet):
    serializer_class   = CropScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CropScan.objects.filter(submitted_by=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        scan = serializer.save(submitted_by=self.request.user, status='pending')
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
            print(f'scan processing error: {e}')

    def destroy(self, request, *args, **kwargs):
        scan = self.get_object()
        if scan.submitted_by != request.user:
            return Response({'error': 'not authorised'}, status=status.HTTP_403_FORBIDDEN)
        scan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
