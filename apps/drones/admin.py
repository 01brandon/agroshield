from django.contrib import admin
from .models import DroneOperator, DroneBooking

@admin.register(DroneOperator)
class DroneOperatorAdmin(admin.ModelAdmin):
    list_display = ['user','drone_type','service_area','price_per_ha','available']

@admin.register(DroneBooking)
class DroneBookingAdmin(admin.ModelAdmin):
    list_display = ['farmer','operator','service_date','total_cost','status']
    list_filter  = ['status']
