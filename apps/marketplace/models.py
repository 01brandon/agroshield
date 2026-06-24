from django.db import models
from django.conf import settings
from apps.farms.models import Farm

class Listing(models.Model):
    STATUS = [('active','Active'),('sold','Sold'),('expired','Expired')]
    GRADE  = [('A','Grade A'),('B','Grade B'),('C','Grade C')]

    farmer       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    farm         = models.ForeignKey(Farm, on_delete=models.CASCADE)
    crop         = models.CharField(max_length=100)
    quantity_kg  = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    grade        = models.CharField(max_length=5, choices=GRADE, default='A')
    description  = models.TextField(blank=True)
    photos       = models.JSONField(default=list)
    is_auction   = models.BooleanField(default=False)
    auction_end  = models.DateTimeField(null=True, blank=True)
    status       = models.CharField(max_length=20, choices=STATUS, default='active')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.crop} {self.quantity_kg}kg'

class Bid(models.Model):
    listing    = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    buyer      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-amount']

class EscrowTransaction(models.Model):
    STATUS = [('held','Held'),('released','Released'),('disputed','Disputed'),('refunded','Refunded')]

    listing         = models.ForeignKey(Listing, on_delete=models.CASCADE)
    buyer           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='escrow_bought')
    seller          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='escrow_sold')
    amount          = models.DecimalField(max_digits=12, decimal_places=2)
    mpesa_reference = models.CharField(max_length=100, blank=True)
    status          = models.CharField(max_length=20, choices=STATUS, default='held')
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'escrow {self.amount} - {self.status}'
