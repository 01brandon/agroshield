from rest_framework import viewsets, permissions
from .models import SoilReading
from .serializers import SoilReadingSerializer

class SoilReadingViewSet(viewsets.ModelViewSet):
    serializer_class   = SoilReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SoilReading.objects.filter(farm__owner=self.request.user)
