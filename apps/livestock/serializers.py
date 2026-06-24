from rest_framework import serializers
from .models import Animal, HealthRecord

class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Animal
        fields = '__all__'
        read_only_fields = ['owner','created_at']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model  = HealthRecord
        fields = '__all__'
        read_only_fields = ['recorded_at']
