from django.contrib import admin
from .models import InsurancePolicy

@admin.register(InsurancePolicy)
class InsurancePolicyAdmin(admin.ModelAdmin):
    list_display = ['farmer','crop','premium','payout_amount','status','end_date']
    list_filter  = ['status']
