from django.contrib import admin
from .models import VoiceInteraction

@admin.register(VoiceInteraction)
class VoiceInteractionAdmin(admin.ModelAdmin):
    list_display = ['phone','farmer','language','duration','created_at']
