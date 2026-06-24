from django.contrib import admin
from .models import Farm

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display  = ['name','owner','primary_crop','size_hectares','location_name','created_at']
    list_filter   = ['primary_crop']
    search_fields = ['name','owner__email','location_name']
