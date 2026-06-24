from django.contrib import admin
from .models import FoodSecurityAlert

@admin.register(FoodSecurityAlert)
class FoodSecurityAlertAdmin(admin.ModelAdmin):
    list_display = ['region','country','severity','risk_score','notified','created_at']
    list_filter  = ['severity','country']
