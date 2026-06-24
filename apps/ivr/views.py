from rest_framework import viewsets, permissions
from .models import VoiceInteraction
from .serializers import VoiceInteractionSerializer

class VoiceInteractionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = VoiceInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VoiceInteraction.objects.filter(farmer=self.request.user)
