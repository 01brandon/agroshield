import os, requests, base64, random
from django.conf import settings

def analyse_crop_image(image_url):
    api_key = getattr(settings, 'OPENAI_API_KEY', '')

    if api_key and 'your_openai' not in api_key:
        try:
            # download image and encode as base64
            img_res = requests.get(image_url, timeout=15)
            if img_res.status_code != 200:
                return _fallback('could not download image')

            encoded   = base64.b64encode(img_res.content).decode('utf-8')
            mime_type = img_res.headers.get('content-type', 'image/jpeg').split(';')[0]

            payload = {
                'model': 'gpt-4o',
                'max_tokens': 600,
                'messages': [{
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url':    f'data:{mime_type};base64,{encoded}',
                                'detail': 'high',
                            }
                        },
                        {
                            'type': 'text',
                            'text': (
                                'you are an expert plant pathologist. analyse this crop image carefully.\n\n'
                                'respond in this exact format and nothing else:\n'
                                'DISEASE: <name of disease, pest, deficiency, or "Healthy Crop">\n'
                                'CONFIDENCE: <number 0-100>\n'
                                'CAUSE: <one sentence explaining what caused this>\n'
                                'TREATMENT: <specific actionable chemical treatment with dosage>\n'
                                'ORGANIC: <specific organic or natural alternative treatment>\n\n'
                                'if the image is not a plant, respond with DISEASE: Not a Plant Image and leave other fields empty.'
                            )
                        }
                    ]
                }]
            }

            res = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json    = payload,
                timeout = 40,
            )

            if res.status_code == 200:
                text = res.json()['choices'][0]['message']['content']
                return _parse_gpt_response(text)

            print(f'openai vision error: {res.status_code} {res.text}')

        except Exception as e:
            print(f'openai vision exception: {e}')

    # only falls through here if no api key at all
    return _fallback('openai api key not configured')


def _parse_gpt_response(text):
    lines    = {}
    for line in text.strip().split('\n'):
        if ':' in line:
            key, _, val = line.partition(':')
            lines[key.strip().upper()] = val.strip()

    disease    = lines.get('DISEASE', 'Unidentified Condition')
    confidence = int(lines.get('CONFIDENCE', '70').replace('%','').strip()) / 100
    treatment  = lines.get('TREATMENT', 'consult a local agronomist for treatment advice.')
    organic    = lines.get('ORGANIC', '')

    is_healthy = 'healthy' in disease.lower()
    status     = 'confirmed' if confidence >= 0.70 else 'pending'

    return {
        'disease_detected': disease,
        'confidence_score': round(min(confidence, 1.0), 2),
        'treatment_advice': treatment,
        'organic_alt':      organic,
        'status':           status,
    }


def _fallback(reason):
    return {
        'disease_detected': 'diagnosis pending',
        'confidence_score': 0.0,
        'treatment_advice': f'automated diagnosis unavailable: {reason}. an agronomist will review shortly.',
        'organic_alt':      '',
        'status':           'pending',
    }
