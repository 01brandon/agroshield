import requests
from celery import shared_task
from django.conf import settings
from .models import WeatherAlert, WeatherReading
from apps.farms.models import Farm

@shared_task
def fetch_weather_for_all_farms():
    # runs every 3 hours - polls openweathermap for every registered farm
    farms   = Farm.objects.select_related('owner').all()
    api_key = getattr(settings, 'OPENWEATHER_API_KEY', '')

    for farm in farms:
        try:
            if api_key and api_key != 'your_openweather_key':
                url  = f'https://api.openweathermap.org/data/2.5/weather?lat={farm.latitude}&lon={farm.longitude}&appid={api_key}&units=metric'
                resp = requests.get(url, timeout=10)

                if resp.status_code == 200:
                    data     = resp.json()
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

                    # check thresholds and fire alerts
                    _check_and_alert(farm, temp, humidity, wind)

        except Exception as e:
            print(f'weather fetch failed for farm {farm.id}: {e}')
            try:
                _simulated_reading(farm)
            except Exception:
                pass
        else:
            if not api_key or api_key == 'your_openweather_key':
                _simulated_reading(farm)

    return f'weather fetched for {farms.count()} farms'


def _check_and_alert(farm, temp, humidity, wind):
    # creates alerts and sends sms if conditions exceed safe thresholds
    from .sms import send_sms_alert

    alerts_to_send = []

    if temp > 38:
        alert = WeatherAlert.objects.create(
            farm       = farm,
            alert_type = 'heat',
            severity   = 4,
            message    = f'extreme heat warning: {temp}c at {farm.name}. reduce irrigation frequency and provide shade where possible.',
            temperature= temp,
            humidity   = humidity,
            wind_speed = wind,
        )
        alerts_to_send.append(alert)

    if humidity > 90:
        alert = WeatherAlert.objects.create(
            farm       = farm,
            alert_type = 'pest',
            severity   = 3,
            message    = f'high humidity {humidity}% at {farm.name}. fungal disease and pest risk is elevated. inspect crops within 24 hours.',
            temperature= temp,
            humidity   = humidity,
            wind_speed = wind,
        )
        alerts_to_send.append(alert)

    if temp < 5:
        alert = WeatherAlert.objects.create(
            farm       = farm,
            alert_type = 'frost',
            severity   = 5,
            message    = f'frost warning: temperature at {temp}c near {farm.name}. protect sensitive crops immediately.',
            temperature= temp,
            humidity   = humidity,
            wind_speed = wind,
        )
        alerts_to_send.append(alert)

    # send sms for each alert if farmer has a phone number
    farmer_phone = farm.owner.phone
    if farmer_phone and alerts_to_send:
        for alert in alerts_to_send:
            send_sms_alert(farmer_phone, f'agroshield alert: {alert.message}')
            alert.notified = True
            alert.save()

def _simulated_reading(farm):
    import random
    from .models import WeatherReading
    return WeatherReading.objects.create(
        farm=farm, temperature=round(random.uniform(20, 30), 1),
        humidity=round(random.uniform(40, 80), 1), wind_speed=round(random.uniform(1, 8), 1),
        rainfall_mm=round(random.uniform(0, 5), 1), description='partly cloudy')
