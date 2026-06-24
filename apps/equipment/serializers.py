from rest_framework import serializers
from .models import EquipmentListing, EquipmentBooking

class EquipmentListingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EquipmentListing
        fields = '__all__'
        read_only_fields = ['owner','created_at']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class EquipmentBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EquipmentBooking
        fields = '__all__'
        read_only_fields = ['renter','created_at']

    def create(self, validated_data):
        validated_data['renter'] = self.context['request'].user
        return super().create(validated_data)
