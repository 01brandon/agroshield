from rest_framework import viewsets, permissions
from .models import NDVIReading
from .serializers import NDVIReadingSerializer

class NDVIReadingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = NDVIReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NDVIReading.objects.filter(farm__owner=self.request.user)
