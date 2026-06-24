from django.db import models
from django.conf import settings
from apps.farms.models import Farm

class LedgerEntry(models.Model):
    TYPES = [('input','Input'),('yield','Yield'),('sale','Sale'),('expense','Expense')]

    farm        = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='ledger_entries')
    farmer      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entry_type  = models.CharField(max_length=20, choices=TYPES)
    description = models.CharField(max_length=300)
    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    date        = models.DateField()
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.farm.name} - {self.entry_type} {self.amount}'
