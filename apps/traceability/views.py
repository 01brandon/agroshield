from rest_framework import viewsets, permissions
from .models import TraceabilityBatch, TraceabilityEntry
from .serializers import BatchSerializer, EntrySerializer

class BatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = TraceabilityBatch.objects.all()
    serializer_class   = BatchSerializer
    permission_classes = [permissions.IsAuthenticated]

class EntryViewSet(viewsets.ModelViewSet):
    queryset           = TraceabilityEntry.objects.all()
    serializer_class   = EntrySerializer
    permission_classes = [permissions.IsAuthenticated]
