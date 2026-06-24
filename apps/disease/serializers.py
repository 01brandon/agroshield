from rest_framework import serializers
from .models import CropScan

class CropScanSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CropScan
        fields = '__all__'
        read_only_fields = ['submitted_by','disease_detected','confidence_score','treatment_advice','organic_alt','reviewed_by','status','created_at']

    def create(self, validated_data):
        validated_data['submitted_by'] = self.context['request'].user
        return super().create(validated_data)
