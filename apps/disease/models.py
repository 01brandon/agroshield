from django.db import models
from django.conf import settings
from apps.farms.models import Farm

class CropScan(models.Model):
    STATUS = [('pending','Pending'),('confirmed','Confirmed'),('disputed','Disputed')]

    farm             = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='scans')
    submitted_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cloudinary_url   = models.URLField()
    notes            = models.TextField(blank=True)
    disease_detected = models.CharField(max_length=200, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    treatment_advice = models.TextField(blank=True)
    organic_alt      = models.TextField(blank=True)
    reviewed_by      = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_scans')
    status           = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.farm.name} - {self.disease_detected or "pending"}'
