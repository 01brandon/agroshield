from rest_framework import serializers
from .models import Listing, Bid, EscrowTransaction

class ListingSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.full_name', read_only=True)
    class Meta:
        model  = Listing
        fields = '__all__'
        read_only_fields = ['farmer', 'status']

class BidSerializer(serializers.ModelSerializer):
    buyer_name = serializers.SerializerMethodField()
    class Meta:
        model  = Bid
        fields = '__all__'
        read_only_fields = ['buyer', 'status']

    def get_buyer_name(self, obj):
        return f'{obj.buyer.first_name} {obj.buyer.last_name}'.strip() or obj.buyer.email

class EscrowSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EscrowTransaction
        fields = '__all__'
        read_only_fields = ['buyer', 'seller', 'status']
