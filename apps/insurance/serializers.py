from rest_framework import serializers
from .models import InsurancePolicy

class InsurancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model  = InsurancePolicy
        fields = '__all__'
        read_only_fields = ['farmer','created_at']

    def create(self, validated_data):
        validated_data['farmer'] = self.context['request'].user
        return super().create(validated_data)
