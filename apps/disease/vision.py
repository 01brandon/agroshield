import base64, requests
from django.conf import settings

PROMPT = (
    'you are an expert plant pathologist. examine this crop image carefully.\n'
    'respond in EXACTLY this format:\n'
    'DISEASE: <specific disease name or "Healthy Crop" or "Not a Plant">\n'
    'CONFIDENCE: <0-100>\n'
    'TREATMENT: <specific chemical treatment with dosage and timing>\n'
    'ORGANIC: <specific organic alternative>\n'
)

def analyse_crop_image(image_url):
    try:
        img_res = requests.get(image_url, timeout=15)
        if img_res.status_code != 200:
            return _fallback('could not download image')
        encoded   = base64.b64encode(img_res.content).decode('utf-8')
        mime_type = img_res.headers.get('content-type', 'image/jpeg').split(';')[0]
    except Exception as e:
        return _fallback(f'image download error: {e}')

    # try gemini first
    gemini_key = getattr(settings, 'GEMINI_API_KEY', '')
    if gemini_key and 'your_gemini' not in gemini_key:
        result = _try_gemini(gemini_key, encoded, mime_type)
        if result:
            return result

    # fall back to openai
    openai_key = getattr(settings, 'OPENAI_API_KEY', '')
    if openai_key and 'your_openai' not in openai_key:
        result = _try_openai(openai_key, encoded, mime_type)
        if result:
            return result

    return _fallback('no working AI key configured — add GEMINI_API_KEY or OPENAI_API_KEY')


def _try_gemini(api_key, encoded, mime_type):
    try:
        res = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}',
            json={
                'contents': [{'parts': [
                    {'inline_data': {'mime_type': mime_type, 'data': encoded}},
                    {'text': PROMPT}
                ]}],
                'generationConfig': {'temperature': 0.1, 'maxOutputTokens': 400}
            },
            headers={'Content-Type': 'application/json'},
            timeout=40,
        )
        if res.status_code == 200:
            text = res.json()['candidates'][0]['content']['parts'][0]['text']
            return _parse(text)
        print(f'gemini error {res.status_code}: {res.text[:100]}')
        return None
    except Exception as e:
        print(f'gemini exception: {e}')
        return None


def _try_openai(api_key, encoded, mime_type):
    try:
        res = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={
                'model': 'gpt-4o',
                'max_tokens': 400,
                'messages': [{'role': 'user', 'content': [
                    {'type': 'image_url', 'image_url': {'url': f'data:{mime_type};base64,{encoded}', 'detail': 'high'}},
                    {'type': 'text', 'text': PROMPT}
                ]}]
            },
            timeout=40,
        )
        if res.status_code == 200:
            return _parse(res.json()['choices'][0]['message']['content'])
        print(f'openai error {res.status_code}: {res.text[:100]}')
        return None
    except Exception as e:
        print(f'openai exception: {e}')
        return None


def _parse(text):
    data = {}
    for line in text.strip().split('\n'):
        if ':' in line:
            k, _, v = line.partition(':')
            data[k.strip().upper()] = v.strip()
    raw  = ''.join(c for c in data.get('CONFIDENCE', '75') if c.isdigit() or c == '.')
    conf = float(raw or '75') / 100
    return {
        'disease_detected': data.get('DISEASE', 'Unidentified Condition'),
        'confidence_score': round(min(conf, 1.0), 2),
        'treatment_advice': data.get('TREATMENT', 'consult a local agronomist.'),
        'organic_alt':      data.get('ORGANIC', ''),
        'status':           'confirmed' if conf >= 0.65 else 'pending',
    }


def _fallback(reason):
    return {
        'disease_detected': 'diagnosis pending',
        'confidence_score': 0.0,
        'treatment_advice': f'automated diagnosis unavailable: {reason}.',
        'organic_alt': '',
        'status': 'pending',
    }
