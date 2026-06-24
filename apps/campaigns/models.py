from django.db import models
from django.conf import settings

class Campaign(models.Model):
    CHANNELS = [('push','Push'),('sms','SMS'),('email','Email')]
    STATUS   = [('draft','Draft'),('scheduled','Scheduled'),('sent','Sent')]

    created_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title        = models.CharField(max_length=300)
    content      = models.TextField()
    channel      = models.CharField(max_length=20, choices=CHANNELS)
    segment      = models.JSONField(default=dict)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at      = models.DateTimeField(null=True, blank=True)
    status       = models.CharField(max_length=20, choices=STATUS, default='draft')
    open_count   = models.IntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
