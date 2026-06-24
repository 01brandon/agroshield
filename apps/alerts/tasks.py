from celery import shared_task
from .models import FoodSecurityAlert
from apps.weather.models import WeatherAlert
from apps.farms.models import Farm

@shared_task
def check_food_security_risk():
    # runs daily - checks for regions with multiple risk factors
    from django.db.models import Count, Avg

    # group weather alerts by farm location and count high-severity ones
    high_risk_farms = Farm.objects.annotate(
        alert_count=Count('weather_alerts')
    ).filter(alert_count__gte=3)

    for farm in high_risk_farms:
        # check if alert already exists for this region today
        existing = FoodSecurityAlert.objects.filter(
            region=farm.location_name
        ).order_by('-created_at').first()

        if not existing:
            FoodSecurityAlert.objects.create(
                region      = farm.location_name,
                country     = farm.owner.country or 'unknown',
                latitude    = farm.latitude,
                longitude   = farm.longitude,
                risk_score  = min(farm.alert_count * 0.2, 1.0),
                severity    = 'high' if farm.alert_count >= 5 else 'medium',
                description = f'{farm.alert_count} weather alerts recorded in {farm.location_name}',
            )

    return f'food security check complete - {high_risk_farms.count()} at-risk regions found'
