from django.contrib import admin
from .models import WeatherAlert, WeatherReading

@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ['farm','alert_type','severity','notified','created_at']
    list_filter  = ['alert_type']

@admin.register(WeatherReading)
class WeatherReadingAdmin(admin.ModelAdmin):
    list_display = ['farm','temperature','humidity','rainfall_mm','recorded_at']
