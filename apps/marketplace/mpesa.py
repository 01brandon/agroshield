import requests
import base64
from datetime import datetime
from django.conf import settings

def get_mpesa_token():
    # gets a bearer token from the daraja api
    key    = settings.MPESA_CONSUMER_KEY
    secret = settings.MPESA_CONSUMER_SECRET

    if key == 'your_mpesa_key':
        return None

    credentials = base64.b64encode(f'{key}:{secret}'.encode()).decode()

    if settings.MPESA_ENV == 'production':
        url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    else:
        url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    res = requests.get(url, headers={'Authorization': f'Basic {credentials}'}, timeout=10)

    if res.status_code == 200:
        return res.json().get('access_token')
    return None


def stk_push(phone_number, amount, account_reference, description):
    # initiates an m-pesa stk push payment to the farmer's phone
    token = get_mpesa_token()
    if not token:
        return {'success': False, 'error': 'mpesa not configured or sandbox credentials invalid'}

    shortcode  = settings.MPESA_SHORTCODE
    passkey    = settings.MPESA_PASSKEY
    timestamp  = datetime.now().strftime('%Y%m%d%H%M%S')
    password   = base64.b64encode(f'{shortcode}{passkey}{timestamp}'.encode()).decode()

    if settings.MPESA_ENV == 'production':
        url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    else:
        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

    # clean phone number - must start with 254
    phone = str(phone_number).replace('+', '').replace(' ', '')
    if phone.startswith('0'):
        phone = '254' + phone[1:]

    payload = {
        'BusinessShortCode': shortcode,
        'Password':          password,
        'Timestamp':         timestamp,
        'TransactionType':   'CustomerPayBillOnline',
        'Amount':            int(amount),
        'PartyA':            phone,
        'PartyB':            shortcode,
        'PhoneNumber':       phone,
        'CallBackURL':       f'{settings.FRONTEND_URL}/api/marketplace/mpesa/callback/',
        'AccountReference':  account_reference,
        'TransactionDesc':   description,
    }

    res = requests.post(
        url,
        json    = payload,
        headers = {'Authorization': f'Bearer {token}'},
        timeout = 30,
    )

    if res.status_code == 200:
        data = res.json()
        return {
            'success':       True,
            'checkout_id':   data.get('CheckoutRequestID'),
            'response_code': data.get('ResponseCode'),
            'message':       data.get('CustomerMessage'),
        }

    return {'success': False, 'error': res.text}


def verify_payment(checkout_request_id):
    # queries the daraja api to check if a payment was completed
    token = get_mpesa_token()
    if not token:
        return {'paid': False}

    shortcode = settings.MPESA_SHORTCODE
    passkey   = settings.MPESA_PASSKEY
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password  = base64.b64encode(f'{shortcode}{passkey}{timestamp}'.encode()).decode()

    if settings.MPESA_ENV == 'production':
        url = 'https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query'
    else:
        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'

    payload = {
        'BusinessShortCode': shortcode,
        'Password':          password,
        'Timestamp':         timestamp,
        'CheckoutRequestID': checkout_request_id,
    }

    res = requests.post(
        url,
        json    = payload,
        headers = {'Authorization': f'Bearer {token}'},
        timeout = 15,
    )

    if res.status_code == 200:
        data        = res.json()
        result_code = data.get('ResultCode')
        return {'paid': result_code == '0', 'result_code': result_code}

    return {'paid': False}
