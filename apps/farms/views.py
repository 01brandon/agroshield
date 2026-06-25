from rest_framework import viewsets, permissions
from .models import Farm
from .serializers import FarmSerializer

class FarmViewSet(viewsets.ModelViewSet):
    serializer_class   = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # return only the current user's farms
        return Farm.objects.filter(owner=self.request.user)
