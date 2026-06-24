from rest_framework import serializers
from .models import Cooperative

class CooperativeSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model  = Cooperative
        fields = '__all__'
        read_only_fields = ['admin','created_at']

    def get_member_count(self, obj):
        return obj.members.count()

    def create(self, validated_data):
        validated_data['admin'] = self.context['request'].user
        return super().create(validated_data)
