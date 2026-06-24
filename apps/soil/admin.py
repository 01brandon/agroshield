from django.contrib import admin
from .models import SoilReading

@admin.register(SoilReading)
class SoilReadingAdmin(admin.ModelAdmin):
    list_display = ['farm','ph','nitrogen','phosphorus','potassium','source','recorded_at']
