from django.contrib import admin
from .models import SeedProduct

@admin.register(SeedProduct)
class SeedProductAdmin(admin.ModelAdmin):
    list_display = ['name','crop_type','price','certified','created_at']
    list_filter  = ['certified']
