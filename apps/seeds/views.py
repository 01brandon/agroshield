from rest_framework import viewsets, permissions
from .models import SeedProduct
from .serializers import SeedProductSerializer

class SeedProductViewSet(viewsets.ModelViewSet):
    queryset           = SeedProduct.objects.all()
    serializer_class   = SeedProductSerializer
    permission_classes = [permissions.IsAuthenticated]
