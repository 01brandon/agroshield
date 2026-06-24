import requests
from celery import shared_task
from django.conf import settings
from .models import WeatherAlert, WeatherReading
from apps.farms.models import Farm

@shared_task
def fetch_weather_for_all_farms():
    # runs every 3 hours via celery beat - polls openweathermap for every farm
    farms = Farm.objects.all()
    api_key = settings.OPENWEATHER_API_KEY if hasattr(settings, 'OPENWEATHER_API_KEY') else None

    for farm in farms:
        try:
            if api_key and api_key != 'your_openweather_key':
                url = f'https://api.openweathermap.org/data/2.5/weather?lat={farm.latitude}&lon={farm.longitude}&appid={api_key}&units=metric'
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    temp     = data['main']['temp']
                    humidity = data['main']['humidity']
                    wind     = data['wind']['speed']
                    desc     = data['weather'][0]['description']

                    WeatherReading.objects.create(
                        farm        = farm,
                        temperature = temp,
                        humidity    = humidity,
                        wind_speed  = wind,
                        rainfall_mm = data.get('rain', {}).get('1h', 0),
                        description = desc,
                    )

                    # check thresholds and create alert if needed
                    if temp > 38:
                        WeatherAlert.objects.create(
                            farm       = farm,
                            alert_type = 'heat',
                            severity   = 4,
                            message    = f'extreme heat warning: {temp}c recorded at {farm.name}',
                            temperature= temp,
                            humidity   = humidity,
                            wind_speed = wind,
                        )
                    if humidity > 90:
                        WeatherAlert.objects.create(
                            farm       = farm,
                            alert_type = 'pest',
                            severity   = 3,
                            message    = f'high humidity {humidity}% - pest risk elevated at {farm.name}',
                            temperature= temp,
                            humidity   = humidity,
                            wind_speed = wind,
                        )
        except Exception as e:
            # log error silently and continue to next farm
            print(f'weather fetch failed for farm {farm.id}: {e}')

    return f'weather fetched for {farms.count()} farms'
