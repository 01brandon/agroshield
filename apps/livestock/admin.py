from django.contrib import admin
from .models import Animal, HealthRecord

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['species','breed','tag_number','farm','created_at']

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['animal','symptom','vet_visited','recorded_at']
