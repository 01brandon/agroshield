from django.db import models
from apps.farms.models import Farm

class SoilReading(models.Model):
    SOURCE = [('manual','Manual'),('sensor','IoT Sensor')]

    farm        = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='soil_readings')
    ph          = models.FloatField()
    nitrogen    = models.FloatField()
    phosphorus  = models.FloatField()
    potassium   = models.FloatField()
    moisture    = models.FloatField(null=True, blank=True)
    source      = models.CharField(max_length=20, choices=SOURCE, default='manual')
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f'{self.farm.name} soil {self.recorded_at}'
