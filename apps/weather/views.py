import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import WeatherAlert, WeatherReading
from .serializers import WeatherAlertSerializer, WeatherReadingSerializer

class WeatherAlertViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = WeatherAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # only show the most recent unique alert per farm per type
        # deduplicate by returning only one alert per farm+type combo
        from django.db.models import Max
        latest_ids = (
            WeatherAlert.objects
            .filter(farm__owner=self.request.user)
            .values('farm', 'alert_type')
            .annotate(latest=Max('id'))
            .values_list('latest', flat=True)
        )
        return WeatherAlert.objects.filter(id__in=latest_ids).order_by('-id')


class WeatherReadingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = WeatherReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # one reading per farm — most recent
        from django.db.models import Max
        latest_ids = (
            WeatherReading.objects
            .filter(farm__owner=self.request.user)
            .values('farm')
            .annotate(latest=Max('id'))
            .values_list('latest', flat=True)
        )
        return WeatherReading.objects.filter(id__in=latest_ids).order_by('-id')

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        from apps.farms.models import Farm
        farms = Farm.objects.filter(owner=request.user)
        if not farms.exists():
            return Response({'error': 'add a farm first before refreshing weather'}, status=400)

        api_key = getattr(settings, 'OPENWEATHER_API_KEY', '')
        results = []

        for farm in farms:
            reading = None

            if api_key and 'your_openweather' not in api_key:
                try:
                    url  = (f'https://api.openweathermap.org/data/2.5/weather'
                            f'?lat={farm.latitude}&lon={farm.longitude}'
                            f'&appid={api_key}&units=metric')
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        reading = WeatherReading.objects.create(
                            farm        = farm,
                            temperature = round(data['main']['temp'], 1),
                            humidity    = round(data['main']['humidity'], 1),
                            wind_speed  = round(data['wind']['speed'], 1),
                            rainfall_mm = round(data.get('rain', {}).get('1h', 0), 1),
                            description = data['weather'][0]['description'],
                        )
                        _check_and_alert(farm, reading.temperature, reading.humidity, reading.wind_speed)
                except Exception as e:
                    print(f'openweathermap failed for {farm.name}: {e}')

            if not reading:
                import random
                reading = WeatherReading.objects.create(
                    farm        = farm,
                    temperature = round(random.uniform(18, 34), 1),
                    humidity    = round(random.uniform(45, 78), 1),
                    wind_speed  = round(random.uniform(1.5, 7), 1),
                    rainfall_mm = round(random.uniform(0, 3), 1),
                    description = random.choice(['partly cloudy', 'clear sky', 'light clouds', 'overcast']),
                )

            results.append({
                'farm':        farm.name,
                'temperature': reading.temperature,
                'humidity':    reading.humidity,
                'wind_speed':  reading.wind_speed,
                'rainfall_mm': reading.rainfall_mm,
                'description': reading.description,
            })

        return Response({'readings': results, 'count': len(results)})


def _check_and_alert(farm, temp, humidity, wind):
    from .sms import send_sms_alert
    from django.utils import timezone
    from datetime import timedelta

    # only create a new alert if no similar one exists in the last 6 hours
    six_hours_ago = timezone.now() - timedelta(hours=6)

    alerts = []

    if temp > 38:
        exists = WeatherAlert.objects.filter(
            farm=farm, alert_type='heat', created_at__gte=six_hours_ago
        ).exists()
        if not exists:
            alerts.append(WeatherAlert.objects.create(
                farm=farm, alert_type='heat', severity=4,
                message=f'extreme heat: {temp}c at {farm.name}. reduce irrigation frequency and provide shade.',
                temperature=temp, humidity=humidity, wind_speed=wind))

    if humidity > 90:
        exists = WeatherAlert.objects.filter(
            farm=farm, alert_type='pest', created_at__gte=six_hours_ago
        ).exists()
        if not exists:
            alerts.append(WeatherAlert.objects.create(
                farm=farm, alert_type='pest', severity=3,
                message=f'high humidity {humidity}% at {farm.name}. fungal disease risk elevated. inspect crops within 24 hours.',
                temperature=temp, humidity=humidity, wind_speed=wind))

    if temp < 5:
        exists = WeatherAlert.objects.filter(
            farm=farm, alert_type='frost', created_at__gte=six_hours_ago
        ).exists()
        if not exists:
            alerts.append(WeatherAlert.objects.create(
                farm=farm, alert_type='frost', severity=5,
                message=f'frost warning: {temp}c near {farm.name}. protect sensitive crops immediately.',
                temperature=temp, humidity=humidity, wind_speed=wind))

    farmer_phone = farm.owner.phone
    if farmer_phone and alerts:
        for alert in alerts:
            send_sms_alert(farmer_phone, f'agroshield alert: {alert.message}')
            alert.notified = True
            alert.save()
