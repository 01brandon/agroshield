from rest_framework import serializers
from .models import NDVIReading

class NDVIReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = NDVIReading
        fields = '__all__'
        read_only_fields = ['recorded_at']
