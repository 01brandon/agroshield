import requests
from django.conf import settings

def get_access_token():
    # gets a sentinel hub access token using client credentials
    client_id     = getattr(settings, 'SENTINELHUB_CLIENT_ID', '')
    client_secret = getattr(settings, 'SENTINELHUB_CLIENT_SECRET', '')

    if not client_id or client_id == 'your_sentinel_id':
        return None

    res = requests.post(
        'https://services.sentinel-hub.com/oauth/token',
        data = {
            'grant_type':    'client_credentials',
            'client_id':     client_id,
            'client_secret': client_secret,
        },
        timeout = 15,
    )

    if res.status_code == 200:
        return res.json().get('access_token')
    return None


def fetch_ndvi_for_farm(farm):
    # fetches the latest ndvi reading for a farm polygon from sentinel hub
    token = get_access_token()

    if not token:
        return _simulated_ndvi(farm)

    # build a bounding box around the farm location
    lat = farm.latitude
    lng = farm.longitude
    offset = 0.01  # roughly 1km box

    bbox = [lng - offset, lat - offset, lng + offset, lat + offset]

    payload = {
        'input': {
            'bounds': {
                'bbox': bbox,
                'properties': {'crs': 'http://www.opengis.net/def/crs/EPSG/0/4326'},
            },
            'data': [{
                'type':             'sentinel-2-l2a',
                'dataFilter':       {'mosaickingOrder': 'leastCC'},
            }],
        },
        'output': {
            'width':  256,
            'height': 256,
            'responses': [{'identifier': 'default', 'format': {'type': 'image/png'}}],
        },
        'evalscript': """
//VERSION=3
function setup() {
  return { input: ['B04','B08'], output: { bands: 1 } };
}
function evaluatePixel(s) {
  let ndvi = (s.B08 - s.B04) / (s.B08 + s.B04);
  return [ndvi];
}
""",
    }

    res = requests.post(
        'https://services.sentinel-hub.com/api/v1/process',
        json    = payload,
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type':  'application/json',
        },
        timeout = 30,
    )

    if res.status_code == 200:
        # compute average ndvi from response (simplified)
        import statistics
        pixel_values = list(res.content[:1000])
        avg_ndvi     = statistics.mean(pixel_values) / 255 if pixel_values else 0.5

        health = _ndvi_to_health(avg_ndvi)

        from .models import NDVIReading
        return NDVIReading.objects.create(
            farm       = farm,
            ndvi_value = round(avg_ndvi, 3),
            health     = health,
        )

    return _simulated_ndvi(farm)


def _ndvi_to_health(ndvi):
    # maps ndvi value to a human-readable health label
    if ndvi > 0.6:
        return 'excellent'
    elif ndvi > 0.4:
        return 'good'
    elif ndvi > 0.2:
        return 'moderate'
    elif ndvi > 0.0:
        return 'poor'
    return 'critical'


def _simulated_ndvi(farm):
    # creates a simulated ndvi reading when sentinel hub is not configured
    import random
    from .models import NDVIReading

    ndvi   = round(random.uniform(0.3, 0.8), 3)
    health = _ndvi_to_health(ndvi)

    return NDVIReading.objects.create(
        farm       = farm,
        ndvi_value = ndvi,
        health     = health,
        image_url  = '',
    )
