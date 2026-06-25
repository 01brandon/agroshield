from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CropScan
from .serializers import CropScanSerializer

class CropScanViewSet(viewsets.ModelViewSet):
    serializer_class   = CropScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # return scans for the current user's farms
        return CropScan.objects.filter(submitted_by=self.request.user)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        # agronomist confirms or disputes a scan result
        scan = self.get_object()
        scan.reviewed_by = request.user
        scan.status      = request.data.get('status', 'confirmed')
        scan.save()
        return Response({'message': 'scan reviewed successfully'})
