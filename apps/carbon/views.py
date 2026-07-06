from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from .models import CarbonActivity
from .serializers import CarbonActivitySerializer

@extend_schema_view(
    list=extend_schema(tags=['carbon'], summary='List all carbon activities for the authenticated user'),
    create=extend_schema(
        tags=['carbon'],
        summary='Log a new sustainable farming activity',
        description='Calculates estimated CO2 tonnes automatically using IPCC coefficients. Activity is auto-verified.',
        examples=[
            OpenApiExample('Agroforestry Example', value={
                'farm': 1, 'practice': 'agroforestry', 'area_hectares': '5.0'
            }, request_only=True),
            OpenApiExample('Response', value={
                'id': 3, 'practice': 'agroforestry', 'area_hectares': '5.00',
                'estimated_tonnes': 12.5, 'verified': True
            }, response_only=True)
        ]
    ),
    retrieve=extend_schema(tags=['carbon'], summary='Retrieve a specific carbon activity'),
    destroy=extend_schema(tags=['carbon'], summary='Delete a carbon activity'),
)
class CarbonActivityViewSet(viewsets.ModelViewSet):
    serializer_class   = CarbonActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CarbonActivity.objects.filter(farmer=self.request.user)
