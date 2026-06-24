from rest_framework import serializers
from .models import CarbonActivity

class CarbonActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model  = CarbonActivity
        fields = '__all__'
        read_only_fields = ['farmer','verified','certificate_url','logged_at']

    def create(self, validated_data):
        validated_data['farmer'] = self.context['request'].user
        return super().create(validated_data)
