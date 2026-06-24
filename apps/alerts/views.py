from rest_framework import viewsets, permissions
from .models import FoodSecurityAlert
from .serializers import FoodSecurityAlertSerializer

class FoodSecurityAlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = FoodSecurityAlert.objects.all()
    serializer_class   = FoodSecurityAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
