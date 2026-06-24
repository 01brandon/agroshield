from rest_framework import viewsets, permissions

class IsAdminOrNGO(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin','ngo']

from .models import Campaign
from .serializers import CampaignSerializer

class CampaignViewSet(viewsets.ModelViewSet):
    queryset           = Campaign.objects.all()
    serializer_class   = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrNGO]
