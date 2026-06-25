import requests
from django.conf import settings

def get_ai_response(question, crop_tag=''):
    # sends a farmer question to openai and returns an expert response
    api_key = getattr(settings, 'OPENAI_API_KEY', '')

    if not api_key or api_key == 'your_openai_key':
        return _fallback_response(question)

    system_prompt = """you are an expert agricultural advisor with 20 years of experience 
helping smallholder farmers in africa. you give practical, actionable advice about crop 
diseases, soil health, weather management, pest control, and farming best practices. 
keep responses concise and easy to understand. use simple language. 
always mention when a farmer should seek an in-person agronomist visit."""

    user_message = f"crop type: {crop_tag or 'not specified'}\n\nfarmer question: {question}"

    try:
        res = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type':  'application/json',
            },
            json = {
                'model':      'gpt-4o-mini',
                'messages':   [
                    {'role': 'system',  'content': system_prompt},
                    {'role': 'user',    'content': user_message},
                ],
                'max_tokens':  400,
                'temperature': 0.7,
            },
            timeout = 30,
        )

        if res.status_code == 200:
            data    = res.json()
            content = data['choices'][0]['message']['content']
            return {'success': True, 'response': content}

        return _fallback_response(question)

    except Exception as e:
        return _fallback_response(question, str(e))


def _fallback_response(question, error=''):
    # returns when openai is unavailable
    return {
        'success':  False,
        'response': 'our ai co-pilot is temporarily unavailable. your question has been posted and a verified agronomist will respond shortly.',
        'error':    error,
    }
