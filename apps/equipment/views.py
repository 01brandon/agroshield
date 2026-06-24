from rest_framework import viewsets, permissions
from .models import EquipmentListing, EquipmentBooking
from .serializers import EquipmentListingSerializer, EquipmentBookingSerializer

class EquipmentListingViewSet(viewsets.ModelViewSet):
    queryset           = EquipmentListing.objects.filter(available=True)
    serializer_class   = EquipmentListingSerializer
    permission_classes = [permissions.IsAuthenticated]

class EquipmentBookingViewSet(viewsets.ModelViewSet):
    serializer_class   = EquipmentBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EquipmentBooking.objects.filter(renter=self.request.user)
