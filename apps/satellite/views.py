from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import NDVIReading
from .serializers import NDVIReadingSerializer

class NDVIReadingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = NDVIReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NDVIReading.objects.filter(farm__owner=self.request.user)

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        # manually triggers a fresh planet scene fetch for all the user's farms
        from apps.farms.models import Farm
        from .planet import fetch_ndvi_for_farm

        farms   = Farm.objects.filter(owner=request.user)
        results = []

        for farm in farms:
            try:
                reading = fetch_ndvi_for_farm(farm)
                results.append({
                    'farm':       farm.name,
                    'ndvi':       reading.ndvi_value,
                    'health':     reading.health,
                })
            except Exception as e:
                results.append({'farm': farm.name, 'error': str(e)})

        return Response({'results': results, 'count': len(results)})
