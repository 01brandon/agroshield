from django.contrib import admin
from .models import CropScan

@admin.register(CropScan)
class CropScanAdmin(admin.ModelAdmin):
    list_display  = ['farm','disease_detected','confidence_score','status','created_at']
    list_filter   = ['status']
    search_fields = ['farm__name','disease_detected']
