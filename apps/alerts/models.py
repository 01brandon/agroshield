from django.db import models

class FoodSecurityAlert(models.Model):
    SEVERITY = [('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')]

    region      = models.CharField(max_length=200)
    country     = models.CharField(max_length=100)
    latitude    = models.FloatField()
    longitude   = models.FloatField()
    risk_score  = models.FloatField()
    severity    = models.CharField(max_length=20, choices=SEVERITY)
    description = models.TextField()
    notified    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.region} - {self.severity}'
