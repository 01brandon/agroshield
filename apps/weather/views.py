from rest_framework import viewsets, permissions
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
