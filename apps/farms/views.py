from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from .models import Farm
from .serializers import FarmSerializer

@extend_schema_view(
    list=extend_schema(tags=['farms'], summary='List all farms belonging to the authenticated user'),
    create=extend_schema(tags=['farms'], summary='Register a new farm', examples=[
        OpenApiExample('Example', value={
            'name': 'Green Valley Farm', 'location_name': 'Nakuru, Kenya',
            'latitude': -0.3031, 'longitude': 36.08,
            'size_hectares': '5.50', 'primary_crop': 'maize',
            'description': 'Family-owned maize farm in the Rift Valley.'
        }, request_only=True)
    ]),
    retrieve=extend_schema(tags=['farms'], summary='Retrieve a specific farm'),
    update=extend_schema(tags=['farms'], summary='Replace all farm fields'),
    partial_update=extend_schema(tags=['farms'], summary='Update specific farm fields'),
    destroy=extend_schema(tags=['farms'], summary='Delete a farm and all associated data'),
)
class FarmViewSet(viewsets.ModelViewSet):
    serializer_class   = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Farm.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
