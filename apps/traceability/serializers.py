from rest_framework import serializers
from .models import TraceabilityBatch, TraceabilityEntry

class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model  = TraceabilityEntry
        fields = '__all__'
        read_only_fields = ['handler','timestamp']

    def create(self, validated_data):
        validated_data['handler'] = self.context['request'].user
        return super().create(validated_data)

class BatchSerializer(serializers.ModelSerializer):
    entries = EntrySerializer(many=True, read_only=True)

    class Meta:
        model  = TraceabilityBatch
        fields = '__all__'
        read_only_fields = ['created_at']
