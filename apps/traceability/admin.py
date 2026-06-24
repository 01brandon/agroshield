from django.contrib import admin
from .models import TraceabilityBatch, TraceabilityEntry

@admin.register(TraceabilityBatch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['listing','created_at']

@admin.register(TraceabilityEntry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ['batch','handler','action','timestamp']
