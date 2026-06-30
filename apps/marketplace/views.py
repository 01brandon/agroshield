from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Listing, Bid, EscrowTransaction
from .serializers import ListingSerializer, BidSerializer, EscrowSerializer

class ListingViewSet(viewsets.ModelViewSet):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Listing.objects.filter(status='active')

    @action(detail=False, methods=['get'])
    def mine(self, request):
        listings = Listing.objects.filter(farmer=request.user)
        return Response(ListingSerializer(listings, many=True).data)

class BidViewSet(viewsets.ModelViewSet):
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Bid.objects.all()
        listing_id = self.request.query_params.get('listing')
        if listing_id:
            qs = qs.filter(listing_id=listing_id)
        return qs

class EscrowViewSet(viewsets.ModelViewSet):
    serializer_class = EscrowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EscrowTransaction.objects.filter(buyer=self.request.user) | EscrowTransaction.objects.filter(seller=self.request.user)

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        escrow = self.get_object()
        escrow.status = 'released'
        escrow.save()
        return Response({'message': 'escrow released'})
