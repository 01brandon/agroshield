from django.contrib import admin
from .models import CarbonActivity

@admin.register(CarbonActivity)
class CarbonActivityAdmin(admin.ModelAdmin):
    list_display = ['farm','practice','estimated_tonnes','verified','logged_at']
    list_filter  = ['verified','practice']
