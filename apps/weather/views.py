from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import WeatherAlert, WeatherReading
from .serializers import WeatherAlertSerializer, WeatherReadingSerializer

class WeatherAlertViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = WeatherAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return WeatherAlert.objects.filter(farm__owner=self.request.user)

class WeatherReadingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = WeatherReadingSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return WeatherReading.objects.filter(farm__owner=self.request.user)

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        from apps.farms.models import Farm
        from .tasks import fetch_weather_for_all_farms
        farms = Farm.objects.filter(owner=request.user)
        if not farms.exists():
            return Response({'error': 'add a farm first'}, status=400)
        fetch_weather_for_all_farms()
        return Response({'message': 'weather refreshed'})
