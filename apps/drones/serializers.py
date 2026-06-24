from rest_framework import serializers
from .models import DroneOperator, DroneBooking

class DroneOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DroneOperator
        fields = '__all__'
        read_only_fields = ['user','rating','created_at']

class DroneBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DroneBooking
        fields = '__all__'
        read_only_fields = ['farmer','created_at']

    def create(self, validated_data):
        validated_data['farmer'] = self.context['request'].user
        return super().create(validated_data)
