from django.db import models
from apps.farms.models import Farm

class NDVIReading(models.Model):
    farm        = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='ndvi_readings')
    ndvi_value  = models.FloatField()
    image_url   = models.URLField(blank=True)
    health      = models.CharField(max_length=20, default='good')
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f'{self.farm.name} ndvi {self.ndvi_value}'
