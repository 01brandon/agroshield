from django.db import models
from django.conf import settings

class Farm(models.Model):
    CROP_CHOICES = [
        ('maize','Maize'),('wheat','Wheat'),('rice','Rice'),
        ('coffee','Coffee'),('tea','Tea'),('cassava','Cassava'),
        ('sorghum','Sorghum'),('beans','Beans'),('other','Other'),
    ]
    owner         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farms')
    name          = models.CharField(max_length=200)
    location_name = models.CharField(max_length=200)
    latitude      = models.FloatField()
    longitude     = models.FloatField()
    size_hectares = models.DecimalField(max_digits=10, decimal_places=2)
    primary_crop  = models.CharField(max_length=50, choices=CROP_CHOICES)
    description   = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.owner.email}'
