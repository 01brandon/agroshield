from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Listing, Bid, EscrowTransaction
from .serializers import ListingSerializer, BidSerializer, EscrowSerializer

class ListingViewSet(viewsets.ModelViewSet):
    serializer_class   = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Listing.objects.filter(status='active')

class BidViewSet(viewsets.ModelViewSet):
    serializer_class   = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bid.objects.filter(buyer=self.request.user)

class EscrowViewSet(viewsets.ModelViewSet):
    serializer_class   = EscrowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            EscrowTransaction.objects.filter(buyer=self.request.user) |
            EscrowTransaction.objects.filter(seller=self.request.user)
        )

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        # releases escrow funds to the seller after delivery confirmed
        escrow        = self.get_object()
        escrow.status = 'released'
        escrow.save()
        return Response({'message': 'escrow released successfully'})

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        # initiates mpesa stk push for this escrow transaction
        escrow = self.get_object()
        phone  = request.data.get('phone') or request.user.phone

        if not phone:
            return Response({'error': 'phone number required'}, status=status.HTTP_400_BAD_REQUEST)

        from .mpesa import stk_push
        result = stk_push(
            phone_number      = phone,
            amount            = escrow.amount,
            account_reference = f'AGRO-{escrow.id}',
            description       = f'agroshield escrow payment for {escrow.listing.crop}',
        )

        if result['success']:
            escrow.mpesa_reference = result.get('checkout_id', '')
            escrow.save()
            return Response({'message': 'payment initiated. check your phone', 'checkout_id': result.get('checkout_id')})

        return Response({'error': result.get('error', 'payment failed')}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def mpesa_callback(self, request):
        # receives mpesa callback after payment is processed
        try:
            body           = request.data.get('Body', {})
            stk_callback   = body.get('stkCallback', {})
            result_code    = stk_callback.get('ResultCode')
            checkout_id    = stk_callback.get('CheckoutRequestID')

            if result_code == 0:
                # payment successful - find and update escrow
                escrow = EscrowTransaction.objects.filter(mpesa_reference=checkout_id).first()
                if escrow:
                    escrow.status = 'held'
                    escrow.save()

            return Response({'ResultCode': 0, 'ResultDesc': 'accepted'})
        except Exception:
            return Response({'ResultCode': 0, 'ResultDesc': 'accepted'})
