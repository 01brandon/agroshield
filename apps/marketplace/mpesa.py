import requests
import base64
from datetime import datetime
from django.conf import settings

# sandbox and production base urls
SANDBOX_URL    = 'https://sandbox.safaricom.co.ke'
PRODUCTION_URL = 'https://api.safaricom.co.ke'

def get_base_url():
    # returns the correct base url based on environment setting
    env = getattr(settings, 'MPESA_ENV', 'sandbox')
    return PRODUCTION_URL if env == 'production' else SANDBOX_URL


def get_mpesa_token():
    # gets a bearer token using consumer key and secret
    key    = getattr(settings, 'MPESA_CONSUMER_KEY', '')
    secret = getattr(settings, 'MPESA_CONSUMER_SECRET', '')

    if not key or key == 'your_mpesa_key':
        return {'success': False, 'token': None, 'error': 'mpesa keys not configured'}

    credentials = base64.b64encode(f'{key}:{secret}'.encode()).decode()
    url         = f'{get_base_url()}/oauth/v1/generate?grant_type=client_credentials'

    try:
        res = requests.get(
            url,
            headers = {'Authorization': f'Basic {credentials}'},
            timeout = 15,
        )

        if res.status_code == 200:
            data = res.json()
            return {'success': True, 'token': data.get('access_token')}

        return {'success': False, 'token': None, 'error': f'token request failed: {res.status_code} {res.text}'}

    except Exception as e:
        return {'success': False, 'token': None, 'error': str(e)}


def generate_password():
    # generates the base64 encoded password required by mpesa express
    shortcode = getattr(settings, 'MPESA_SHORTCODE', '')
    passkey   = getattr(settings, 'MPESA_PASSKEY', '')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    raw       = f'{shortcode}{passkey}{timestamp}'
    password  = base64.b64encode(raw.encode()).decode()
    return password, timestamp


def format_phone(phone_number):
    # converts any kenyan phone format to the 2547XXXXXXXX format mpesa requires
    phone = str(phone_number).strip().replace(' ', '').replace('-', '')

    if phone.startswith('+254'):
        phone = phone[1:]  # remove the + sign
    elif phone.startswith('0'):
        phone = '254' + phone[1:]  # replace leading 0 with 254
    elif phone.startswith('7') or phone.startswith('1'):
        phone = '254' + phone  # add country code

    return phone


def stk_push(phone_number, amount, account_reference, description):
    # initiates an mpesa express stk push - prompts the buyer to enter their pin
    token_result = get_mpesa_token()

    if not token_result['success']:
        return {'success': False, 'error': token_result['error']}

    token     = token_result['token']
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
        res = requests.post(
            f'{get_base_url()}/mpesa/stkpush/v1/processrequest',
            json    = payload,
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type':  'application/json',
            },
            timeout = 30,
        )

        data = res.json()

        if res.status_code == 200 and data.get('ResponseCode') == '0':
            return {
                'success':       True,
                'checkout_id':   data.get('CheckoutRequestID'),
                'merchant_id':   data.get('MerchantRequestID'),
                'response_code': data.get('ResponseCode'),
                'message':       data.get('CustomerMessage', 'check your phone to complete payment'),
            }

        return {
            'success': False,
            'error':   data.get('errorMessage') or data.get('ResponseDescription') or f'mpesa error: {res.text}',
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def stk_query(checkout_request_id):
    # checks the status of a pending stk push transaction
    token_result = get_mpesa_token()

    if not token_result['success']:
        return {'paid': False, 'error': token_result['error']}

    token     = token_result['token']
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
                'Authorization': f'Bearer {token}',
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
    # sends money from business to customer - used for payouts to farmers
    # requires a separate b2c api activation on the developer portal
    token_result = get_mpesa_token()

    if not token_result['success']:
        return {'success': False, 'error': token_result['error']}

    token     = token_result['token']
    shortcode = getattr(settings, 'MPESA_SHORTCODE', '')
    phone     = format_phone(phone_number)
    callback  = getattr(settings, 'MPESA_CALLBACK_URL', 'http://localhost:8000/api/marketplace/mpesa/callback/')

    payload = {
        'InitiatorName':      'agroshield',
        'SecurityCredential': '',
        'CommandID':          'BusinessPayment',
        'Amount':             int(float(amount)),
        'PartyA':             shortcode,
        'PartyB':             phone,
        'Remarks':            remarks[:100],
        'QueueTimeOutURL':    callback,
        'ResultURL':          callback,
        'Occasion':           'escrow release',
    }

    try:
        res  = requests.post(
            f'{get_base_url()}/mpesa/b2c/v3/paymentrequest',
            json    = payload,
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type':  'application/json',
            },
            timeout = 30,
        )

        data = res.json()

        if res.status_code == 200:
            return {
                'success':          True,
                'conversation_id':  data.get('ConversationID'),
                'originator_id':    data.get('OriginatorConversationID'),
                'response_code':    data.get('ResponseCode'),
                'message':          data.get('ResponseDescription'),
            }

        return {'success': False, 'error': data.get('errorMessage', res.text)}

    except Exception as e:
        return {'success': False, 'error': str(e)}
