from django.db import models
from apps.farms.models import Farm

class WeatherAlert(models.Model):
    ALERT_TYPES = [('drought','Drought'),('flood','Flood'),('frost','Frost'),('pest','Pest'),('heat','Heat')]

    farm        = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='weather_alerts')
    alert_type  = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity    = models.IntegerField(default=1)
    message     = models.TextField()
    temperature = models.FloatField(null=True, blank=True)
    humidity    = models.FloatField(null=True, blank=True)
    wind_speed  = models.FloatField(null=True, blank=True)
    notified    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.farm.name} - {self.alert_type}'

class WeatherReading(models.Model):
    farm        = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='weather_readings')
    temperature = models.FloatField()
    humidity    = models.FloatField()
    wind_speed  = models.FloatField()
    rainfall_mm = models.FloatField(default=0)
    description = models.CharField(max_length=200)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f'{self.farm.name} reading {self.recorded_at}'
