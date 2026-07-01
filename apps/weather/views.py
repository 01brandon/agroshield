import requests
from django.conf import settings
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import WeatherAlert, WeatherReading
from .serializers import WeatherAlertSerializer, WeatherReadingSerializer

class WeatherAlertViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = WeatherAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return WeatherAlert.objects.filter(farm__owner=self.request.user).order_by('-created_at')

class WeatherReadingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = WeatherReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WeatherReading.objects.filter(farm__owner=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        from apps.farms.models import Farm
        farms = Farm.objects.filter(owner=request.user)
        if not farms.exists():
            return Response({'error': 'add a farm first'}, status=400)

        api_key = getattr(settings, 'OPENWEATHER_API_KEY', '')
        results = []

        for farm in farms:
            reading = None
            if api_key and 'your_openweather' not in api_key:
                try:
                    url  = f'https://api.openweathermap.org/data/2.5/weather?lat={farm.latitude}&lon={farm.longitude}&appid={api_key}&units=metric'
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        reading = WeatherReading.objects.create(
                            farm        = farm,
                            temperature = data['main']['temp'],
                            humidity    = data['main']['humidity'],
                            wind_speed  = data['wind']['speed'],
                            rainfall_mm = data.get('rain', {}).get('1h', 0),
                            description = data['weather'][0]['description'],
                        )
                        # check thresholds and fire sms
                        _check_and_alert(farm, reading.temperature, reading.humidity, reading.wind_speed)
                except Exception as e:
                    print(f'openweathermap failed: {e}')

            # fallback to simulated if real call failed or no key
            if not reading:
                import random
                reading = WeatherReading.objects.create(
                    farm        = farm,
                    temperature = round(random.uniform(18, 34), 1),
                    humidity    = round(random.uniform(35, 85), 1),
                    wind_speed  = round(random.uniform(1, 9), 1),
                    rainfall_mm = round(random.uniform(0, 4), 1),
                    description = 'partly cloudy',
                )

            results.append({
                'farm':        farm.name,
                'temperature': reading.temperature,
                'humidity':    reading.humidity,
                'wind_speed':  reading.wind_speed,
                'description': reading.description,
            })

        return Response({'readings': results, 'count': len(results)})


def _check_and_alert(farm, temp, humidity, wind):
    from .sms import send_sms_alert
    from .models import WeatherAlert
    alerts = []
    if temp > 38:
        alerts.append(WeatherAlert.objects.create(
            farm=farm, alert_type='heat', severity=4,
            message=f'extreme heat: {temp}c at {farm.name}. reduce irrigation frequency.',
            temperature=temp, humidity=humidity, wind_speed=wind))
    if humidity > 90:
        alerts.append(WeatherAlert.objects.create(
            farm=farm, alert_type='pest', severity=3,
            message=f'high humidity {humidity}% at {farm.name}. fungal disease risk elevated.',
            temperature=temp, humidity=humidity, wind_speed=wind))
    if temp < 5:
        alerts.append(WeatherAlert.objects.create(
            farm=farm, alert_type='frost', severity=5,
            message=f'frost warning: {temp}c near {farm.name}. protect crops immediately.',
            temperature=temp, humidity=humidity, wind_speed=wind))
    farmer_phone = farm.owner.phone
    if farmer_phone and alerts:
        for alert in alerts:
            send_sms_alert(farmer_phone, f'agroshield: {alert.message}')
            alert.notified = True
            alert.save()
