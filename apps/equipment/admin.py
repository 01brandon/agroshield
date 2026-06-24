from django.contrib import admin
from .models import EquipmentListing, EquipmentBooking

@admin.register(EquipmentListing)
class EquipmentListingAdmin(admin.ModelAdmin):
    list_display = ['name','owner','daily_rate','location','available']

@admin.register(EquipmentBooking)
class EquipmentBookingAdmin(admin.ModelAdmin):
    list_display = ['equipment','renter','start_date','end_date','total_cost','status']
    list_filter  = ['status']
