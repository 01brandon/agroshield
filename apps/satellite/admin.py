from django.contrib import admin
from .models import NDVIReading

@admin.register(NDVIReading)
class NDVIAdmin(admin.ModelAdmin):
    list_display = ['farm','ndvi_value','health','recorded_at']
