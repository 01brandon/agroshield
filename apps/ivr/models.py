from django.db import models
from django.conf import settings

class VoiceInteraction(models.Model):
    farmer     = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    phone      = models.CharField(max_length=20)
    transcript = models.TextField()
    response   = models.TextField()
    language   = models.CharField(max_length=10, default='en')
    duration   = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'ivr {self.phone} {self.created_at}'
