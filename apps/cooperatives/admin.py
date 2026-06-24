from django.contrib import admin
from .models import Cooperative

@admin.register(Cooperative)
class CooperativeAdmin(admin.ModelAdmin):
    list_display = ['name','admin','location','created_at']
