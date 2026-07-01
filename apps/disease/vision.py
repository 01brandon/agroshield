import requests, base64
from django.conf import settings

def analyse_crop_image(image_url):
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        return _fallback('gemini api key not configured — add GEMINI_API_KEY to your environment variables')
    try:
        img_res = requests.get(image_url, timeout=15)
        if img_res.status_code != 200:
            return _fallback('could not download image for analysis')
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
            }],
            'generationConfig': {
                'maxOutputTokens': 600,
                'temperature':     0.2,
            }
        }
        res = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent?key={api_key}',
            headers = {'Content-Type': 'application/json'},
            json    = payload,
            timeout = 40,
        )
        if res.status_code == 200:
            data = res.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            return _parse_response(text)
        print(f'gemini vision error: {res.status_code} {res.text}')
        return _fallback(f'gemini api returned {res.status_code}')
    except Exception as e:
        print(f'gemini vision exception: {e}')
        return _fallback(str(e))

def _parse_response(text):
    lines = {}
    for line in text.strip().split('\n'):
        if ':' in line:
            key, _, val = line.partition(':')
            lines[key.strip().upper()] = val.strip()
    disease    = lines.get('DISEASE', 'Unidentified Condition')
    confidence = int(lines.get('CONFIDENCE', '70').replace('%', '').strip()) / 100
    treatment  = lines.get('TREATMENT', 'consult a local agronomist for treatment advice.')
    organic    = lines.get('ORGANIC', '')
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
