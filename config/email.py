from django.conf import settings

def send_email(to_email, subject, body_text, body_html=None):
    # sends a transactional email via sendgrid
    api_key = getattr(settings, 'SENDGRID_API_KEY', '')

    if not api_key or api_key == 'your_sendgrid_key':
        # fall back to django console backend
        print(f'[EMAIL TO {to_email}] subject: {subject}\n{body_text}')
        return {'success': True, 'simulated': True}

    import requests

    payload = {
        'personalizations': [{'to': [{'email': to_email}]}],
        'from':             {'email': settings.DEFAULT_FROM_EMAIL},
        'subject':          subject,
        'content':          [
            {'type': 'text/plain', 'value': body_text},
        ],
    }

    if body_html:
        payload['content'].append({'type': 'text/html', 'value': body_html})

    res = requests.post(
        'https://api.sendgrid.com/v3/mail/send',
        json    = payload,
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type':  'application/json',
        },
        timeout = 15,
    )

    return {'success': res.status_code == 202}


def send_welcome_email(user):
    send_email(
        to_email   = user.email,
        subject    = 'welcome to agroshield',
        body_text  = f'hi {user.first_name},\n\nwelcome to agroshield. your account is ready.\n\nvisit http://localhost:8000/dashboard/ to get started.\n\nthe agroshield team',
        body_html  = f'<h2>welcome to agroshield, {user.first_name}</h2><p>your account is ready. <a href="http://localhost:8000/dashboard/">get started here</a></p>',
    )


def send_alert_email(user, alert):
    send_email(
        to_email  = user.email,
        subject   = f'agroshield alert: {alert.alert_type} at {alert.farm.name}',
        body_text = f'hi {user.first_name},\n\n{alert.message}\n\nlog in to your dashboard for more details.\n\nthe agroshield team',
    )
