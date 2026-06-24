from rest_framework import viewsets, permissions
from .models import Cooperative
from .serializers import CooperativeSerializer

class CooperativeViewSet(viewsets.ModelViewSet):
    queryset           = Cooperative.objects.all()
    serializer_class   = CooperativeSerializer
    permission_classes = [permissions.IsAuthenticated]
