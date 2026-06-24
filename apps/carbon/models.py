from django.db import models
from django.conf import settings
from apps.farms.models import Farm

class CarbonActivity(models.Model):
    PRACTICES = [('cover_crop','Cover Cropping'),('agroforestry','Agroforestry'),('no_till','No-Till'),('composting','Composting')]

    farm             = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='carbon_activities')
    farmer           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    practice         = models.CharField(max_length=50, choices=PRACTICES)
    area_hectares    = models.FloatField()
    estimated_tonnes = models.FloatField()
    evidence_url     = models.URLField(blank=True)
    verified         = models.BooleanField(default=False)
    certificate_url  = models.URLField(blank=True)
    logged_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.farm.name} - {self.practice}'
