from rest_framework import serializers
from .models import FoodSecurityAlert

class FoodSecurityAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FoodSecurityAlert
        fields = '__all__'
        read_only_fields = ['created_at']
