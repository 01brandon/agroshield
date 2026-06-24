from rest_framework import viewsets, permissions
from .models import InsurancePolicy
from .serializers import InsurancePolicySerializer

class InsurancePolicyViewSet(viewsets.ModelViewSet):
    serializer_class   = InsurancePolicySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InsurancePolicy.objects.filter(farmer=self.request.user)
