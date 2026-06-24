from django.db import models
from django.conf import settings

class DroneOperator(models.Model):
    user         = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    drone_type   = models.CharField(max_length=100)
    service_area = models.CharField(max_length=200)
    price_per_ha = models.DecimalField(max_digits=8, decimal_places=2)
    available    = models.BooleanField(default=True)
    rating       = models.FloatField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - drone operator'

class DroneBooking(models.Model):
    STATUS = [('pending','Pending'),('confirmed','Confirmed'),('completed','Completed'),('cancelled','Cancelled')]

    operator      = models.ForeignKey(DroneOperator, on_delete=models.CASCADE)
    farmer        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service_date  = models.DateField()
    area_hectares = models.FloatField()
    total_cost    = models.DecimalField(max_digits=10, decimal_places=2)
    status        = models.CharField(max_length=20, choices=STATUS, default='pending')
    notes         = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.farmer.email} booking {self.service_date}'
