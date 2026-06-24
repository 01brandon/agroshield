from rest_framework import serializers
from .models import SeedProduct

class SeedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SeedProduct
        fields = '__all__'
        read_only_fields = ['seller','created_at']

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)
