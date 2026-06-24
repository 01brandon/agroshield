from celery import shared_task
from django.utils import timezone
from .models import Campaign

@shared_task
def send_scheduled_campaigns():
    # runs every 30 minutes - sends any campaigns due for delivery
    now      = timezone.now()
    pending  = Campaign.objects.filter(status='scheduled', scheduled_at__lte=now)

    for campaign in pending:
        try:
            # placeholder - connect twilio/sendgrid/firebase here
            campaign.status  = 'sent'
            campaign.sent_at = now
            campaign.save()
        except Exception as e:
            print(f'campaign {campaign.id} failed: {e}')

    return f'{pending.count()} campaigns sent'
