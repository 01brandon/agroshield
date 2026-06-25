import os
import requests
import base64

def get_gcp_token():
    # uses application default credentials - works with gcloud auth login
    # no service account key file needed
    try:
        # try metadata server first (works on gcp compute instances)
        meta_res = requests.get(
            'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',
            headers = {'Metadata-Flavor': 'Google'},
            timeout = 2,
        )
        if meta_res.status_code == 200:
            return meta_res.json()['access_token']
    except Exception:
        pass

    # fall back to application default credentials file
    creds_path = os.environ.get(
        'GOOGLE_APPLICATION_CREDENTIALS',
        os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
    )

    if not os.path.exists(creds_path):
        return None

    try:
        import json
        with open(creds_path) as f:
            creds = json.load(f)

        cred_type = creds.get('type')

        if cred_type == 'authorized_user':
            # this is a personal google account credential from gcloud auth login
            token_res = requests.post(
                'https://oauth2.googleapis.com/token',
                data = {
                    'client_id':     creds['client_id'],
                    'client_secret': creds['client_secret'],
                    'refresh_token': creds['refresh_token'],
                    'grant_type':    'refresh_token',
                },
                timeout = 10,
            )
            if token_res.status_code == 200:
                return token_res.json()['access_token']

        elif cred_type == 'service_account':
            # service account json - use jwt flow
            import time
            try:
                import jwt
            except ImportError:
                return None

            now     = int(time.time())
            payload = {
                'iss': creds['client_email'],
                'sub': creds['client_email'],
                'aud': 'https://oauth2.googleapis.com/token',
                'iat': now,
                'exp': now + 3600,
                'scope': 'https://www.googleapis.com/auth/cloud-platform',
            }

            signed    = jwt.encode(payload, creds['private_key'], algorithm='RS256')
            token_res = requests.post(
                'https://oauth2.googleapis.com/token',
                data = {
                    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                    'assertion':  signed,
                },
                timeout = 10,
            )

            if token_res.status_code == 200:
                return token_res.json()['access_token']

    except Exception as e:
        print(f'gcp token error: {e}')

    return None


def analyse_crop_image(image_url):
    # downloads image from cloudinary then sends to google cloud vision
    try:
        img_response = requests.get(image_url, timeout=15)
        if img_response.status_code != 200:
            return _fallback('could not download image from url')

        token = get_gcp_token()
        if not token:
            return _fallback('gcp credentials not found - run: gcloud auth application-default login')

        encoded = base64.b64encode(img_response.content).decode('utf-8')

        payload = {
            'requests': [{
                'image':    {'content': encoded},
                'features': [
                    {'type': 'LABEL_DETECTION', 'maxResults': 10},
                    {'type': 'IMAGE_PROPERTIES', 'maxResults': 5},
                ],
            }]
        }

        res = requests.post(
            'https://vision.googleapis.com/v1/images:annotate',
            json    = payload,
            headers = {'Authorization': f'Bearer {token}'},
            timeout = 30,
        )

        if res.status_code != 200:
            return _fallback(f'vision api returned {res.status_code}: {res.text}')

        labels = res.json()['responses'][0].get('labelAnnotations', [])
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


def _map_labels_to_disease(labels):
    label_names = [l['description'].lower() for l in labels]
    scores      = {l['description'].lower(): l['score'] for l in labels}

    disease_map = {
        'blight': (
            'Northern Corn Leaf Blight',
            'apply mancozeb fungicide at 2.5kg per hectare every 14 days. remove infected leaves.',
            'neem oil spray at 5ml per litre of water every 7 days.',
        ),
        'rust': (
            'Wheat Leaf Rust',
            'apply trifloxystrobin fungicide at label rate.',
            'use resistant varieties next season. apply potassium bicarbonate spray weekly.',
        ),
        'mosaic': (
            'Cassava Mosaic Virus',
            'remove and destroy infected plants. control whitefly with imidacloprid.',
            'plant virus-free certified cuttings only.',
        ),
        'wilt': (
            'Fusarium Wilt',
            'apply copper-based fungicide to soil. ensure proper crop rotation.',
            'solarise soil before planting. apply trichoderma biocontrol to roots.',
        ),
        'spot': (
            'Cercospora Leaf Spot',
            'apply azoxystrobin fungicide at 1 litre per hectare every 21 days.',
            'apply compost tea spray weekly.',
        ),
        'mite': (
            'Spider Mite Infestation',
            'apply abamectin miticide. spray undersides of leaves thoroughly.',
            'spray cold water on leaf undersides daily. introduce predatory mites.',
        ),
        'yellow': (
            'Nitrogen Deficiency',
            'apply urea at 50kg per hectare in split applications.',
            'apply well-rotted compost at 5 tonnes per hectare.',
        ),
        'aphid': (
            'Aphid Infestation',
            'apply lambda-cyhalothrin insecticide at label rate.',
            'spray diluted dish soap solution weekly. plant marigolds nearby.',
        ),
        'healthy': (
            'No Disease Detected',
            'your crop appears healthy. maintain current practices.',
            'continue organic practices and monitor weekly.',
        ),
    }

    for keyword, (disease, treatment, organic) in disease_map.items():
        for label in label_names:
            if keyword in label:
                conf = scores.get(label, 0.8)
                return disease, conf, treatment, organic

    plant_keywords = ['plant','leaf','crop','agriculture','field','green','farm']
    is_plant       = any(kw in label_names for kw in plant_keywords)

    if is_plant:
        return (
            'Unidentified Stress Condition',
            0.6,
            'no specific disease identified. submit a clearer close-up of affected leaves.',
            'maintain optimal nutrition and watering. monitor over next 3-5 days.',
        )

    return (
        'Not a Plant Image',
        0.0,
        'the image does not appear to show a crop. photograph affected leaves in good lighting.',
        'ensure the image shows the affected plant part clearly.',
    )


def _fallback(reason):
    return {
        'disease_detected': 'diagnosis pending',
        'confidence_score': 0.0,
        'treatment_advice': f'automated diagnosis unavailable: {reason}. an agronomist will review shortly.',
        'organic_alt':      '',
        'status':           'pending',
        'raw_labels':       [],
    }
