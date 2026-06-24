from django.contrib import admin
from .models import Campaign

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['title','channel','status','scheduled_at','open_count','created_at']
    list_filter  = ['channel','status']
