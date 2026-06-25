import os
import requests
from django.conf import settings

def analyse_crop_image(image_url):
    # downloads the image from cloudinary then sends it to google cloud vision
    # returns disease name, confidence, treatment advice

    try:
        # download image bytes from cloudinary url
        img_response = requests.get(image_url, timeout=15)
        if img_response.status_code != 200:
            return _fallback('could not download image from url')

        image_bytes = img_response.content

        # build the vision api request
        api_url = f'https://vision.googleapis.com/v1/images:annotate'

        # get access token from service account
        token = get_gcp_token()
        if not token:
            return _fallback('gcp authentication failed - check service_account.json')

        import base64
        encoded = base64.b64encode(image_bytes).decode('utf-8')

        payload = {
            'requests': [{
                'image': {'content': encoded},
                'features': [
                    {'type': 'LABEL_DETECTION',    'maxResults': 10},
                    {'type': 'IMAGE_PROPERTIES',   'maxResults': 5},
                    {'type': 'SAFE_SEARCH_DETECTION'},
                ],
            }]
        }

        res = requests.post(
            api_url,
            json    = payload,
            headers = {'Authorization': f'Bearer {token}'},
            timeout = 30,
        )

        if res.status_code != 200:
            return _fallback(f'vision api returned {res.status_code}')

        data   = res.json()
        labels = data['responses'][0].get('labelAnnotations', [])

        # map vision labels to known plant diseases
        disease, confidence, treatment, organic = _map_labels_to_disease(labels)

        return {
            'disease_detected': disease,
            'confidence_score': confidence,
            'treatment_advice': treatment,
            'organic_alt':      organic,
            'status':           'confirmed' if confidence > 0.75 else 'pending',
            'raw_labels':       [l['description'] for l in labels[:5]],
        }

    except Exception as e:
        return _fallback(str(e))


def get_gcp_token():
    # gets a short-lived bearer token from the service account json file
    try:
        import json
        import time
        import jwt

        sa_path = os.path.join(settings.BASE_DIR, 'service_account.json')
        if not os.path.exists(sa_path):
            return None

        with open(sa_path) as f:
            sa = json.load(f)

        now     = int(time.time())
        payload = {
            'iss': sa['client_email'],
            'sub': sa['client_email'],
            'aud': 'https://oauth2.googleapis.com/token',
            'iat': now,
            'exp': now + 3600,
            'scope': 'https://www.googleapis.com/auth/cloud-platform',
        }

        signed = jwt.encode(payload, sa['private_key'], algorithm='RS256')

        token_res = requests.post('https://oauth2.googleapis.com/token', data={
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion':  signed,
        }, timeout=10)

        if token_res.status_code == 200:
            return token_res.json()['access_token']

        return None

    except Exception:
        return None


def _map_labels_to_disease(labels):
    # maps google vision labels to plant disease diagnoses
    label_names = [l['description'].lower() for l in labels]
    scores      = {l['description'].lower(): l['score'] for l in labels}

    disease_map = {
        'blight': (
            'Northern Corn Leaf Blight',
            'apply mancozeb fungicide at 2.5kg per hectare every 14 days. remove and destroy infected leaves immediately.',
            'neem oil spray at 5ml per litre of water every 7 days. ensure good field drainage.',
        ),
        'rust': (
            'Wheat Leaf Rust',
            'apply trifloxystrobin fungicide at label rate. spray early morning when dew is present.',
            'use resistant varieties next season. apply potassium bicarbonate spray weekly.',
        ),
        'mosaic': (
            'Cassava Mosaic Virus',
            'no chemical cure. remove and destroy infected plants immediately to prevent spread. control whitefly vectors with imidacloprid.',
            'plant virus-free certified cuttings only. introduce natural whitefly predators.',
        ),
        'wilt': (
            'Fusarium Wilt',
            'apply copper-based fungicide to soil at planting. ensure proper crop rotation every 3 seasons.',
            'solarise soil before planting. apply trichoderma biocontrol product to roots.',
        ),
        'spot': (
            'Cercospora Leaf Spot',
            'apply azoxystrobin fungicide at 1 litre per hectare. repeat every 21 days.',
            'apply compost tea spray weekly. improve air circulation by reducing plant density.',
        ),
        'mite': (
            'Spider Mite Infestation',
            'apply abamectin miticide at label rate. spray undersides of leaves thoroughly.',
            'spray cold water on undersides of leaves daily. introduce predatory mites.',
        ),
        'yellow': (
            'Nitrogen Deficiency / Yellowing',
            'apply urea at 50kg per hectare. split application over 2 weeks.',
            'apply well-rotted compost at 5 tonnes per hectare. use green manure cover crops.',
        ),
        'aphid': (
            'Aphid Infestation',
            'apply lambda-cyhalothrin insecticide at label rate. target growing tips.',
            'spray diluted dish soap solution weekly. plant marigolds as companion plants.',
        ),
        'healthy': (
            'No Disease Detected',
            'your crop appears healthy. maintain current practices.',
            'continue organic practices. monitor weekly for early signs of stress.',
        ),
    }

    # check each label against known diseases
    for keyword, (disease, treatment, organic) in disease_map.items():
        for label in label_names:
            if keyword in label:
                conf = scores.get(label, 0.8)
                return disease, conf, treatment, organic

    # check if it looks like a plant at all
    plant_keywords = ['plant','leaf','crop','agriculture','field','green','farm']
    is_plant       = any(kw in label_names for kw in plant_keywords)

    if is_plant:
        return (
            'Unidentified Stress Condition',
            0.6,
            'the image shows plant stress but no specific disease was identified. submit a clearer close-up of affected leaves for better diagnosis.',
            'maintain optimal soil nutrition and watering. monitor over next 3-5 days.',
        )

    return (
        'Not a Plant Image',
        0.0,
        'the submitted image does not appear to show a crop. please photograph the affected leaves clearly in good lighting.',
        'ensure the image shows the affected plant part clearly.',
    )


def _fallback(reason):
    # returns when the api call fails for any reason
    return {
        'disease_detected': 'diagnosis pending',
        'confidence_score': 0.0,
        'treatment_advice': f'automated diagnosis is temporarily unavailable: {reason}. an agronomist will review your scan shortly.',
        'organic_alt':      '',
        'status':           'pending',
        'raw_labels':       [],
    }
