from celery import shared_task
from apps.farms.models import Farm

@shared_task
def fetch_ndvi_for_all_farms():
    # runs every 5 days - fetches ndvi readings for all registered farms via planet
    farms = Farm.objects.all()

    for farm in farms:
        try:
            from .planet import fetch_ndvi_for_farm
            fetch_ndvi_for_farm(farm)
        except Exception as e:
            print(f'planet ndvi fetch failed for farm {farm.id}: {e}')

    return f'ndvi fetched for {farms.count()} farms via planet'
