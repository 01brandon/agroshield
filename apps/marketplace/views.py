from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Listing, Bid, EscrowTransaction
from .serializers import ListingSerializer, BidSerializer, EscrowSerializer

class ListingViewSet(viewsets.ModelViewSet):
    serializer_class   = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Listing.objects.filter(status='active')

    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)

    @action(detail=False, methods=['get'])
    def mine(self, request):
        listings = Listing.objects.filter(farmer=request.user)
        return Response(ListingSerializer(listings, many=True).data)


class BidViewSet(viewsets.ModelViewSet):
    serializer_class   = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs         = Bid.objects.select_related('buyer', 'listing').all()
        listing_id = self.request.query_params.get('listing')
        if listing_id:
            qs = qs.filter(listing_id=listing_id)
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        listing = serializer.validated_data['listing']
        # prevent bidding on own listing
        if listing.farmer == self.request.user:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('you cannot bid on your own listing')
        serializer.save(buyer=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        bid     = self.get_object()
        listing = bid.listing
        # only the listing owner can accept
        if listing.farmer != request.user:
            return Response({'error': 'only the listing owner can accept bids'}, status=403)
        bid.status     = 'accepted'
        listing.status = 'sold'
        bid.save()
        listing.save()
        # create escrow
        EscrowTransaction.objects.create(
            listing = listing,
            buyer   = bid.buyer,
            seller  = listing.farmer,
            amount  = bid.amount,
            status  = 'pending',
        )
        return Response({'message': f'bid of ksh {bid.amount} accepted. escrow created.'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        bid = self.get_object()
        if bid.listing.farmer != request.user:
            return Response({'error': 'only the listing owner can reject bids'}, status=403)
        bid.status = 'rejected'
        bid.save()
        return Response({'message': 'bid rejected'})


class EscrowViewSet(viewsets.ModelViewSet):
    serializer_class   = EscrowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (EscrowTransaction.objects.filter(buyer=self.request.user) |
                EscrowTransaction.objects.filter(seller=self.request.user))

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        escrow = self.get_object()
        escrow.status = 'released'
        escrow.save()
        return Response({'message': 'escrow released to seller'})
