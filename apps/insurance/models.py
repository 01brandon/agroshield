from django.db import models
from django.conf import settings
from apps.farms.models import Farm

class InsurancePolicy(models.Model):
    STATUS = [('active','Active'),('claimed','Claimed'),('expired','Expired')]

    farmer        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    farm          = models.ForeignKey(Farm, on_delete=models.CASCADE)
    crop          = models.CharField(max_length=100)
    premium       = models.DecimalField(max_digits=10, decimal_places=2)
    payout_amount = models.DecimalField(max_digits=12, decimal_places=2)
    trigger_type  = models.CharField(max_length=50)
    trigger_value = models.FloatField()
    start_date    = models.DateField()
    end_date      = models.DateField()
    status        = models.CharField(max_length=20, choices=STATUS, default='active')
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.farmer.email} - {self.crop} policy'
