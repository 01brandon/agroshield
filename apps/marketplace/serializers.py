from rest_framework import serializers
from .models import Listing, Bid, EscrowTransaction

class ListingSerializer(serializers.ModelSerializer):
    farmer_name = serializers.ReadOnlyField(source='farmer.full_name')

    class Meta:
        model  = Listing
        fields = '__all__'
        read_only_fields = ['farmer','created_at']

    def create(self, validated_data):
        validated_data['farmer'] = self.context['request'].user
        return super().create(validated_data)

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Bid
        fields = '__all__'
        read_only_fields = ['buyer','created_at']

    def create(self, validated_data):
        validated_data['buyer'] = self.context['request'].user
        return super().create(validated_data)

class EscrowSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EscrowTransaction
        fields = '__all__'
        read_only_fields = ['created_at']
