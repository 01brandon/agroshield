import base64, requests
from django.conf import settings

def analyse_crop_image(image_url):
    api_key = getattr(settings, 'GEMINI_API_KEY', '')

    if not api_key or 'your_gemini' in api_key:
        return _fallback('gemini api key not configured')

    try:
        img_res = requests.get(image_url, timeout=15)
        if img_res.status_code != 200:
            return _fallback('could not download image')

        encoded   = base64.b64encode(img_res.content).decode('utf-8')
        mime_type = img_res.headers.get('content-type', 'image/jpeg').split(';')[0]

        payload = {
            'contents': [{
                'parts': [
                    {
                        'inline_data': {
                            'mime_type': mime_type,
                            'data':      encoded,
                        }
                    },
                    {
                        'text': (
                            'you are an expert plant pathologist. look at this crop image carefully and diagnose it.\n'
                            'respond in EXACTLY this format and nothing else:\n'
                            'DISEASE: <specific disease name, pest, deficiency, or "Healthy Crop" or "Not a Plant">\n'
                            'CONFIDENCE: <number between 0 and 100>\n'
                            'CAUSE: <one sentence explaining the cause>\n'
                            'TREATMENT: <specific chemical treatment with exact dosage and timing>\n'
                            'ORGANIC: <specific organic or natural alternative with method>\n'
                        )
                    }
                ]
            }],
            'generationConfig': {
                'temperature':     0.1,
                'maxOutputTokens': 500,
            }
        }

        res = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}',
            json    = payload,
            headers = {'Content-Type': 'application/json'},
            timeout = 40,
        )

        if res.status_code == 200:
            text = res.json()['candidates'][0]['content']['parts'][0]['text']
            return _parse(text)

        return _fallback(f'gemini returned {res.status_code}: {res.text[:120]}')

    except Exception as e:
        return _fallback(str(e))


def _parse(text):
    data = {}
    for line in text.strip().split('\n'):
        if ':' in line:
            k, _, v = line.partition(':')
            data[k.strip().upper()] = v.strip()

    raw_conf = ''.join(filter(lambda c: c.isdigit() or c == '.', data.get('CONFIDENCE', '75')))
    conf     = float(raw_conf or '75') / 100

    return {
        'disease_detected': data.get('DISEASE', 'Unidentified Condition'),
        'confidence_score': round(min(conf, 1.0), 2),
        'treatment_advice': data.get('TREATMENT', 'consult a local agronomist for advice.'),
        'organic_alt':      data.get('ORGANIC', ''),
        'status':           'confirmed' if conf >= 0.65 else 'pending',
    }


def _fallback(reason):
    return {
        'disease_detected': 'diagnosis pending',
        'confidence_score': 0.0,
        'treatment_advice': f'automated diagnosis unavailable: {reason}. an agronomist will review shortly.',
        'organic_alt':      '',
        'status':           'pending',
    }
