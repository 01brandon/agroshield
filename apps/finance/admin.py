from django.contrib import admin
from .models import LedgerEntry

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ['farm','entry_type','description','amount','date']
    list_filter  = ['entry_type']
