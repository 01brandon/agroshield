from rest_framework import viewsets, permissions
from .models import CarbonActivity
from .serializers import CarbonActivitySerializer

class CarbonActivityViewSet(viewsets.ModelViewSet):
    serializer_class   = CarbonActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CarbonActivity.objects.filter(farmer=self.request.user)
