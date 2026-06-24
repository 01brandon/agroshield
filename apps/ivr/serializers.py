from rest_framework import serializers
from .models import VoiceInteraction

class VoiceInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VoiceInteraction
        fields = '__all__'
        read_only_fields = ['created_at']
