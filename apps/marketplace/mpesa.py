import requests
import base64
from datetime import datetime
from django.conf import settings

SANDBOX_URL    = 'https://sandbox.safaricom.co.ke'
PRODUCTION_URL = 'https://api.safaricom.co.ke'

def get_base_url():
    env = getattr(settings, 'MPESA_ENV', 'sandbox')
    return PRODUCTION_URL if env == 'production' else SANDBOX_URL


def get_mpesa_token():
    key    = getattr(settings, 'MPESA_CONSUMER_KEY', '')
    secret = getattr(settings, 'MPESA_CONSUMER_SECRET', '')

    if not key or 'your_mpesa' in key:
        return {'success': False, 'token': None, 'error': 'mpesa keys not configured'}

    credentials = base64.b64encode(f'{key}:{secret}'.encode()).decode()

    try:
        res = requests.get(
            f'{get_base_url()}/oauth/v1/generate?grant_type=client_credentials',
            headers = {'Authorization': f'Basic {credentials}'},
            timeout = 15,
        )

        if res.status_code == 200:
            return {'success': True, 'token': res.json().get('access_token')}

        return {'success': False, 'token': None, 'error': f'{res.status_code}: {res.text}'}

    except Exception as e:
        return {'success': False, 'token': None, 'error': str(e)}


def generate_password():
    shortcode = getattr(settings, 'MPESA_SHORTCODE', '')
    passkey   = getattr(settings, 'MPESA_PASSKEY', '')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    raw       = f'{shortcode}{passkey}{timestamp}'
    password  = base64.b64encode(raw.encode()).decode()
    return password, timestamp


def format_phone(phone_number):
    phone = str(phone_number).strip().replace(' ', '').replace('-', '')
    if phone.startswith('+254'):
        phone = phone[1:]
    elif phone.startswith('0'):
        phone = '254' + phone[1:]
    elif phone.startswith('7') or phone.startswith('1'):
        phone = '254' + phone
    return phone


def stk_push(phone_number, amount, account_reference, description):
    # initiates mpesa express stk push - buyer pays into escrow
    token_result = get_mpesa_token()
    if not token_result['success']:
        return {'success': False, 'error': token_result['error']}

    password, timestamp = generate_password()
    shortcode = getattr(settings, 'MPESA_SHORTCODE', '')
    callback  = getattr(settings, 'MPESA_CALLBACK_URL', 'http://localhost:8000/api/marketplace/mpesa/callback/')
    phone     = format_phone(phone_number)

    payload = {
        'BusinessShortCode': shortcode,
        'Password':          password,
        'Timestamp':         timestamp,
        'TransactionType':   'CustomerPayBillOnline',
        'Amount':            int(float(amount)),
        'PartyA':            phone,
        'PartyB':            shortcode,
        'PhoneNumber':       phone,
        'CallBackURL':       callback,
        'AccountReference':  account_reference[:12],
        'TransactionDesc':   description[:13],
    }

    try:
        res  = requests.post(
            f'{get_base_url()}/mpesa/stkpush/v1/processrequest',
            json    = payload,
            headers = {
                'Authorization': f'Bearer {token_result["token"]}',
                'Content-Type':  'application/json',
            },
            timeout = 30,
        )

        data = res.json()

        if res.status_code == 200 and data.get('ResponseCode') == '0':
            return {
                'success':     True,
                'checkout_id': data.get('CheckoutRequestID'),
                'merchant_id': data.get('MerchantRequestID'),
                'message':     data.get('CustomerMessage', 'check your phone to complete payment'),
            }

        return {
            'success': False,
            'error':   data.get('errorMessage') or data.get('ResponseDescription') or res.text,
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def stk_query(checkout_request_id):
    # checks if the buyer completed their stk push payment
    token_result = get_mpesa_token()
    if not token_result['success']:
        return {'paid': False, 'error': token_result['error']}

    password, timestamp = generate_password()
    shortcode = getattr(settings, 'MPESA_SHORTCODE', '')

    payload = {
        'BusinessShortCode': shortcode,
        'Password':          password,
        'Timestamp':         timestamp,
        'CheckoutRequestID': checkout_request_id,
    }

    try:
        res  = requests.post(
            f'{get_base_url()}/mpesa/stkpushquery/v1/query',
            json    = payload,
            headers = {
                'Authorization': f'Bearer {token_result["token"]}',
                'Content-Type':  'application/json',
            },
            timeout = 15,
        )

        data        = res.json()
        result_code = str(data.get('ResultCode', ''))

        return {
            'paid':        result_code == '0',
            'result_code': result_code,
            'description': data.get('ResultDesc', ''),
        }

    except Exception as e:
        return {'paid': False, 'error': str(e)}


def b2c_payment(phone_number, amount, remarks):
    # sends money from agroshield business to farmer after delivery confirmed
    # uses the security credential generated from the safaricom developer portal
    token_result = get_mpesa_token()
    if not token_result['success']:
        return {'success': False, 'error': token_result['error']}

    shortcode           = getattr(settings, 'MPESA_SHORTCODE', '')
    security_credential = getattr(settings, 'MPESA_SECURITY_CREDENTIAL', '')
    callback            = getattr(settings, 'MPESA_CALLBACK_URL', 'http://localhost:8000/api/marketplace/mpesa/callback/')
    phone               = format_phone(phone_number)

    if not security_credential:
        return {
            'success': False,
            'error':   'mpesa security credential not configured. go to developer.safaricom.co.ke and generate it.',
        }

    payload = {
        'InitiatorName':          'testapi',
        'SecurityCredential':     security_credential,
        'CommandID':              'BusinessPayment',
        'Amount':                 int(float(amount)),
        'PartyA':                 shortcode,
        'PartyB':                 phone,
        'Remarks':                remarks[:100],
        'QueueTimeOutURL':        callback,
        'ResultURL':              callback,
        'Occasion':               'escrow payout',
    }

    try:
        res  = requests.post(
            f'{get_base_url()}/mpesa/b2c/v3/paymentrequest',
            json    = payload,
            headers = {
                'Authorization': f'Bearer {token_result["token"]}',
                'Content-Type':  'application/json',
            },
            timeout = 30,
        )

        data = res.json()

        if res.status_code == 200 and data.get('ResponseCode') == '0':
            return {
                'success':         True,
                'conversation_id': data.get('ConversationID'),
                'originator_id':   data.get('OriginatorConversationID'),
                'message':         data.get('ResponseDescription'),
            }

        return {
            'success': False,
            'error':   data.get('errorMessage') or data.get('ResponseDescription') or res.text,
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}
