from rest_framework import viewsets, permissions
from .models import DroneOperator, DroneBooking
from .serializers import DroneOperatorSerializer, DroneBookingSerializer

class DroneOperatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = DroneOperator.objects.filter(available=True)
    serializer_class   = DroneOperatorSerializer
    permission_classes = [permissions.IsAuthenticated]

class DroneBookingViewSet(viewsets.ModelViewSet):
    serializer_class   = DroneBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DroneBooking.objects.filter(farmer=self.request.user)
