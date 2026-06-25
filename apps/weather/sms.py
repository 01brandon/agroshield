from django.conf import settings

def send_sms_alert(phone_number, message):
    # sends an sms alert to a farmer via twilio
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    auth_token  = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')

    if not account_sid or account_sid == 'your_twilio_sid':
        # twilio not configured - log to console instead
        print(f'[SMS WOULD BE SENT TO {phone_number}]: {message}')
        return {'success': True, 'simulated': True}

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)

        msg = client.messages.create(
            body = message,
            from_= from_number,
            to   = phone_number,
        )

        return {'success': True, 'sid': msg.sid}

    except Exception as e:
        return {'success': False, 'error': str(e)}


def send_bulk_sms(phone_numbers, message):
    # sends the same sms to multiple farmers
    results = []
    for phone in phone_numbers:
        result = send_sms_alert(phone, message)
        results.append({'phone': phone, **result})
    return results
