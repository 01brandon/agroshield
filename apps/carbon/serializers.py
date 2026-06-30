from rest_framework import serializers
from .models import CarbonActivity

class CarbonActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonActivity
        fields = '__all__'
        read_only_fields = ['farmer', 'verified', 'certificate_url', 'logged_at']

    def create(self, validated_data):
        validated_data['farmer'] = self.context['request'].user
        coefficients = {'cover_crop': 0.3, 'agroforestry': 2.5, 'no_till': 0.5, 'composting': 0.8}
        practice = validated_data.get('practice')
        area = float(validated_data.get('area_hectares', 0))
        validated_data['estimated_tonnes'] = round(area * coefficients.get(practice, 0.3), 2)
        validated_data['verified'] = True
        return super().create(validated_data)
