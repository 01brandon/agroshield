from django.db import models
from django.conf import settings

class SeedProduct(models.Model):
    seller      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name        = models.CharField(max_length=200)
    crop_type   = models.CharField(max_length=100)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    quantity    = models.IntegerField()
    unit        = models.CharField(max_length=20, default='kg')
    certified   = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    photo       = models.URLField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
