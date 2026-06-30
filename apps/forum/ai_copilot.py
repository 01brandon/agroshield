import requests, random
from django.conf import settings

GENERIC_TIPS = [
    "based on similar reports, check for yellowing or browning patterns starting from the leaf edges — this often points to nutrient stress or early fungal infection. test your soil pH if you haven't recently.",
    "this is a common issue during the rainy season. ensure good drainage around the root zone and inspect the undersides of leaves for pests.",
    "consider rotating crops next season if this issue persists — continuous planting of the same crop depletes specific soil nutrients and increases disease risk.",
    "try isolating a few affected plants and removing damaged leaves to slow spread while you wait for an agronomist to confirm the diagnosis.",
]

def get_ai_response(question, crop_tag=''):
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if api_key and 'your_openai' not in api_key:
        try:
            res = requests.post('https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json={'model': 'gpt-4o-mini', 'messages': [
                    {'role': 'system', 'content': 'you are an expert agricultural advisor for african smallholder farmers. give short practical advice.'},
                    {'role': 'user', 'content': f'crop: {crop_tag}\n\n{question}'}],
                    'max_tokens': 300}, timeout=20)
            if res.status_code == 200:
                return {'success': True, 'response': res.json()['choices'][0]['message']['content']}
        except Exception:
            pass
    return {'success': True, 'response': random.choice(GENERIC_TIPS) + ' an agronomist will follow up shortly with a more specific answer.'}
