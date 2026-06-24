from django.contrib import admin
from .models import Listing, Bid, EscrowTransaction

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['crop','farmer','quantity_kg','price_per_kg','status','created_at']
    list_filter  = ['status','grade']

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['listing','buyer','amount','created_at']

@admin.register(EscrowTransaction)
class EscrowAdmin(admin.ModelAdmin):
    list_display = ['listing','buyer','seller','amount','status','created_at']
    list_filter  = ['status']
