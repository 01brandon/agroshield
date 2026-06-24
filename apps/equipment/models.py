from django.db import models
from django.conf import settings

class EquipmentListing(models.Model):
    owner       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name        = models.CharField(max_length=200)
    description = models.TextField()
    daily_rate  = models.DecimalField(max_digits=10, decimal_places=2)
    location    = models.CharField(max_length=200)
    photos      = models.JSONField(default=list)
    available   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} by {self.owner.email}'

class EquipmentBooking(models.Model):
    STATUS = [('pending','Pending'),('confirmed','Confirmed'),('returned','Returned')]

    equipment  = models.ForeignKey(EquipmentListing, on_delete=models.CASCADE)
    renter     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='equipment_rentals')
    start_date = models.DateField()
    end_date   = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status     = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.renter.email} renting {self.equipment.name}'
