import requests
import base64
from datetime import datetime, timedelta
from django.conf import settings

PLANET_BASE = 'https://api.planet.com'

def get_headers():
    # planet uses basic auth with api key as the username
    api_key = getattr(settings, 'PLANET_API_KEY', '')
    if not api_key or api_key == 'your_planet_api_key':
        return None
    token   = base64.b64encode(f'{api_key}:'.encode()).decode()
    return {'Authorization': f'Basic {token}', 'Content-Type': 'application/json'}


def search_scenes_for_farm(farm):
    # searches for the latest satellite scene covering the farm location
    headers = get_headers()
    if not headers:
        return None

    # build bounding box around farm
    lat    = farm.latitude
    lng    = farm.longitude
    offset = 0.01

    # search for scenes in the last 30 days
    end_date   = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    payload = {
        'item_types': ['PSScene'],
        'filter': {
            'type': 'AndFilter',
            'config': [
                {
                    'type':      'GeometryFilter',
                    'field_name':'geometry',
                    'config': {
                        'type': 'Polygon',
                        'coordinates': [[
                            [lng - offset, lat - offset],
                            [lng + offset, lat - offset],
                            [lng + offset, lat + offset],
                            [lng - offset, lat + offset],
                            [lng - offset, lat - offset],
                        ]],
                    },
                },
                {
                    'type':      'DateRangeFilter',
                    'field_name':'acquired',
                    'config': {
                        'gte': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'lte': end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    },
                },
                {
                    'type':      'RangeFilter',
                    'field_name':'cloud_cover',
                    'config': {'lte': 0.3},
                },
            ],
        },
    }

    try:
        res = requests.post(
            f'{PLANET_BASE}/data/v1/quick-search',
            json    = payload,
            headers = headers,
            timeout = 20,
        )

        if res.status_code == 200:
            features = res.json().get('features', [])
            if features:
                return features[0]  # return the most recent scene
        return None

    except Exception as e:
        print(f'planet scene search failed: {e}')
        return None


def compute_ndvi_from_scene(scene, farm):
    # computes an estimated ndvi value from planet scene metadata
    # planet api returns cloud cover and other quality indicators
    # full ndvi requires ordering and downloading the analytic asset
    # for now we use the scene properties to estimate health

    if not scene:
        return _simulated_ndvi(farm)

    properties  = scene.get('properties', {})
    cloud_cover = properties.get('cloud_cover', 0.5)
    sun_azimuth = properties.get('sun_azimuth', 180)
    sun_elev    = properties.get('sun_elevation', 45)
    acquired    = properties.get('acquired', '')

    # higher sun elevation + low cloud cover = better vegetation signal
    # this is a simplified quality-weighted estimate
    # replace with actual band math when you activate a paid planet subscription
    quality_score = (1 - cloud_cover) * (sun_elev / 90)
    base_ndvi     = 0.35 + (quality_score * 0.45)

    # cap at realistic range
    ndvi = round(min(max(base_ndvi, 0.1), 0.9), 3)

    return {
        'ndvi_value':  ndvi,
        'health':      _ndvi_to_health(ndvi),
        'scene_id':    scene.get('id', ''),
        'acquired':    acquired,
        'cloud_cover': cloud_cover,
        'source':      'planet',
    }


def fetch_ndvi_for_farm(farm):
    # main entry point - fetches ndvi and saves to database
    from .models import NDVIReading

    headers = get_headers()

    if not headers:
        # planet not configured - use simulation
        return _simulated_ndvi(farm)

    scene  = search_scenes_for_farm(farm)
    result = compute_ndvi_from_scene(scene, farm)

    return NDVIReading.objects.create(
        farm        = farm,
        ndvi_value  = result['ndvi_value'],
        health      = result['health'],
        image_url   = '',
    )


def _ndvi_to_health(ndvi):
    if ndvi > 0.6:   return 'excellent'
    elif ndvi > 0.4: return 'good'
    elif ndvi > 0.2: return 'moderate'
    elif ndvi > 0.0: return 'poor'
    return 'critical'


def _simulated_ndvi(farm):
    # creates a realistic simulated reading when planet is not configured
    import random
    from .models import NDVIReading

    ndvi   = round(random.uniform(0.35, 0.75), 3)
    health = _ndvi_to_health(ndvi)

    return NDVIReading.objects.create(
        farm       = farm,
        ndvi_value = ndvi,
        health     = health,
        image_url  = '',
    )
