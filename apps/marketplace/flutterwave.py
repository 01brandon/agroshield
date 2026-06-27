import requests
import hashlib
import hmac
import json
from django.conf import settings

FLW_BASE = 'https://api.flutterwave.com/v3'

def get_headers():
    secret = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', '')
    if not secret or 'your_secret' in secret:
        return None
    return {
        'Authorization': f'Bearer {secret}',
        'Content-Type':  'application/json',
    }

def initiate_card_payment(amount, currency, email, phone, name, listing_id, redirect_url):
    # initiates a flutterwave card or mobile money payment
    headers = get_headers()
    if not headers:
        return {'success': False, 'error': 'flutterwave not configured', 'simulated': True}

    payload = {
        'tx_ref':       f'AGRO-{listing_id}-{__import__("time").time_ns()}',
        'amount':       str(amount),
        'currency':     currency or 'KES',
        'redirect_url': redirect_url,
        'customer': {
            'email':       email,
            'phonenumber': phone,
            'name':        name,
        },
        'customizations': {
            'title':       'AgroShield',
            'description': 'farm produce payment',
            'logo':        'https://res.cloudinary.com/agroshield/logo.png',
        },
        'payment_options': 'card,mobilemoneykenya,mpesa',
    }

    try:
        res  = requests.post(f'{FLW_BASE}/payments', json=payload, headers=headers, timeout=20)
        data = res.json()

        if res.status_code == 200 and data.get('status') == 'success':
            return {
                'success':      True,
                'payment_link': data['data']['link'],
                'tx_ref':       payload['tx_ref'],
            }

        return {'success': False, 'error': data.get('message', 'payment initiation failed')}

    except Exception as e:
        return {'success': False, 'error': str(e)}


def verify_payment(transaction_id):
    # verifies a completed flutterwave transaction
    headers = get_headers()
    if not headers:
        return {'paid': False, 'error': 'flutterwave not configured'}

    try:
        res  = requests.get(f'{FLW_BASE}/transactions/{transaction_id}/verify', headers=headers, timeout=15)
        data = res.json()

        if res.status_code == 200 and data.get('status') == 'success':
            tx     = data['data']
            paid   = tx.get('status') == 'successful' and tx.get('charge_response_code') == '00'
            return {
                'paid':     paid,
                'amount':   tx.get('amount'),
                'currency': tx.get('currency'),
                'tx_ref':   tx.get('tx_ref'),
            }

        return {'paid': False, 'error': data.get('message')}

    except Exception as e:
        return {'paid': False, 'error': str(e)}


def verify_webhook(payload_body, signature):
    # verifies that a webhook actually came from flutterwave
    secret = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', '')
    computed = hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature)
