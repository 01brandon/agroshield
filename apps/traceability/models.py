from django.db import models
from django.conf import settings
from apps.marketplace.models import Listing

class TraceabilityBatch(models.Model):
    listing    = models.OneToOneField(Listing, on_delete=models.CASCADE)
    qr_code    = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'batch for {self.listing}'

class TraceabilityEntry(models.Model):
    ACTIONS = [('harvested','Harvested'),('transported','Transported'),('processed','Processed'),('sold','Sold')]

    batch     = models.ForeignKey(TraceabilityBatch, on_delete=models.CASCADE, related_name='entries')
    handler   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action    = models.CharField(max_length=30, choices=ACTIONS)
    latitude  = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    notes     = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
