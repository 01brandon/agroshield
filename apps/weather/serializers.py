from rest_framework import serializers
from .models import WeatherAlert, WeatherReading

class WeatherAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WeatherAlert
        fields = '__all__'

class WeatherReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WeatherReading
        fields = '__all__'
