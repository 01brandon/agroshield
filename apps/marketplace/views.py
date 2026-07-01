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
        # show all own listings including sold ones
        listings = Listing.objects.filter(farmer=request.user)
        return Response(ListingSerializer(listings, many=True).data)


class BidViewSet(viewsets.ModelViewSet):
    serializer_class   = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Bid.objects.select_related('buyer','listing').all()
        listing_id = self.request.query_params.get('listing')
        if listing_id:
            qs = qs.filter(listing_id=listing_id)
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        listing = serializer.validated_data['listing']
        if listing.farmer == self.request.user:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'you cannot bid on your own listing'})
        serializer.save(buyer=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        bid = self.get_object()
        if bid.listing.farmer != request.user:
            return Response({'detail': 'only the listing owner can accept bids'}, status=403)
        bid.status           = 'accepted'
        bid.listing.status   = 'sold'
        bid.save()
        bid.listing.save()
        EscrowTransaction.objects.create(
            listing=bid.listing, buyer=bid.buyer,
            seller=bid.listing.farmer, amount=bid.amount, status='pending',
        )
        return Response({'message': f'bid of ksh {bid.amount} accepted. escrow created for buyer to pay.'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        bid = self.get_object()
        if bid.listing.farmer != request.user:
            return Response({'detail': 'only the listing owner can reject bids'}, status=403)
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
    def pay(self, request, pk=None):
        escrow = self.get_object()
        if escrow.buyer != request.user:
            return Response({'detail': 'only the buyer can initiate payment'}, status=403)
        phone = request.data.get('phone') or request.user.phone
        if not phone:
            return Response({'detail': 'phone number required'}, status=400)
        from .mpesa import stk_push
        result = stk_push(phone_number=phone, amount=escrow.amount,
                           account_reference=f'AGRO{escrow.id}', description='agroshield payment')
        if result['success']:
            escrow.mpesa_reference = result.get('checkout_id', '')
            escrow.save()
            return Response({'message': 'check your phone and enter your m-pesa pin'})
        return Response({'detail': result.get('error', 'payment failed')}, status=400)

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        escrow = self.get_object()
        if escrow.buyer != request.user:
            return Response({'detail': 'only the buyer can confirm delivery'}, status=403)
        escrow.status = 'released'
        escrow.save()
        return Response({'message': 'funds released to seller'})
