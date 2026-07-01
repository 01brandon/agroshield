from rest_framework import serializers
from .models import WeatherAlert, WeatherReading

class WeatherReadingSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    class Meta:
        model  = WeatherReading
        fields = '__all__'

class WeatherAlertSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    class Meta:
        model  = WeatherAlert
        fields = '__all__'
