from rest_framework import viewsets, permissions
from .models import Animal, HealthRecord
from .serializers import AnimalSerializer, HealthRecordSerializer

class AnimalViewSet(viewsets.ModelViewSet):
    serializer_class   = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Animal.objects.filter(owner=self.request.user)

class HealthRecordViewSet(viewsets.ModelViewSet):
    serializer_class   = HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HealthRecord.objects.filter(animal__owner=self.request.user)
