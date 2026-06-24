from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import LedgerEntry
from .serializers import LedgerEntrySerializer

class LedgerEntryViewSet(viewsets.ModelViewSet):
    serializer_class   = LedgerEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LedgerEntry.objects.filter(farmer=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        qs      = self.get_queryset()
        income  = qs.filter(entry_type__in=['sale','yield']).aggregate(t=Sum('amount'))['t'] or 0
        expense = qs.filter(entry_type__in=['input','expense']).aggregate(t=Sum('amount'))['t'] or 0
        return Response({'income': income, 'expenses': expense, 'profit': income - expense})
