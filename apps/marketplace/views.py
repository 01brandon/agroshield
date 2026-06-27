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
    def pay(self, request, pk=None):
        # step 1 - buyer initiates payment via mpesa express stk push
        escrow = self.get_object()
        phone  = request.data.get('phone') or request.user.phone

        if not phone:
            return Response(
                {'error': 'phone number is required to initiate mpesa payment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from .mpesa import stk_push
        result = stk_push(
            phone_number      = phone,
            amount            = escrow.amount,
            account_reference = f'AGRO{escrow.id}',
            description       = f'{escrow.listing.crop} payment',
        )

        if result['success']:
            escrow.mpesa_reference = result.get('checkout_id', '')
            escrow.save()
            return Response({
                'message':     result.get('message', 'check your phone and enter your mpesa pin'),
                'checkout_id': result.get('checkout_id'),
            })

        return Response(
            {'error': result.get('error', 'payment initiation failed')},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def check_payment(self, request, pk=None):
        # step 2 - poll to see if the buyer completed the mpesa payment
        escrow = self.get_object()

        if not escrow.mpesa_reference:
            return Response({'paid': False, 'error': 'no payment initiated yet'})

        from .mpesa import stk_query
        result = stk_query(escrow.mpesa_reference)

        if result.get('paid'):
            escrow.status = 'held'
            escrow.save()

        return Response({
            'paid':        result.get('paid'),
            'description': result.get('description'),
        })

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        # step 3 - after delivery confirmed, release funds to farmer via b2c
        escrow = self.get_object()

        if escrow.status != 'held':
            return Response(
                {'error': f'cannot release escrow with status: {escrow.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        seller_phone = escrow.seller.phone
        if not seller_phone:
            return Response(
                {'error': 'seller has no phone number registered for mpesa payout'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from .mpesa import b2c_payment
        result = b2c_payment(
            phone_number = seller_phone,
            amount       = escrow.amount,
            remarks      = f'agroshield payment for {escrow.listing.crop}',
        )

        if result['success']:
            escrow.status = 'released'
            escrow.save()
            return Response({'message': 'funds released to seller via mpesa', 'details': result})

        # b2c not activated yet - just mark as released manually
        escrow.status = 'released'
        escrow.save()
        return Response({'message': 'escrow marked as released. mpesa payout: ' + result.get('error', '')})

    @action(detail=True, methods=['post'])
    def dispute(self, request, pk=None):
        # marks an escrow as disputed - admin reviews manually
        escrow        = self.get_object()
        escrow.status = 'disputed'
        escrow.save()
        return Response({'message': 'escrow marked as disputed. our team will review within 24 hours.'})

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def mpesa_callback(self, request):
        # receives the automatic callback from safaricom after payment completes
        try:
            body         = request.data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            result_code  = stk_callback.get('ResultCode')
            checkout_id  = stk_callback.get('CheckoutRequestID')

            if str(result_code) == '0':
                # payment successful - update escrow status to held
                escrow = EscrowTransaction.objects.filter(
                    mpesa_reference=checkout_id
                ).first()

                if escrow:
                    escrow.status = 'held'
                    escrow.save()

            # always return 200 to safaricom so they stop retrying
            return Response({'ResultCode': 0, 'ResultDesc': 'accepted'})

        except Exception:
            return Response({'ResultCode': 0, 'ResultDesc': 'accepted'})


class FlutterwavePaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def initiate(self, request):
        # initiates a flutterwave card or mobile money payment for an escrow
        escrow_id    = request.data.get('escrow_id')
        redirect_url = request.data.get('redirect_url', 'http://localhost:8000/dashboard/marketplace/')

        try:
            escrow = EscrowTransaction.objects.get(id=escrow_id, buyer=request.user)
        except EscrowTransaction.DoesNotExist:
            return Response({'error': 'escrow not found'}, status=status.HTTP_404_NOT_FOUND)

        from .flutterwave import initiate_card_payment
        result = initiate_card_payment(
            amount       = escrow.amount,
            currency     = 'KES',
            email        = request.user.email,
            phone        = request.user.phone or '',
            name         = request.user.full_name,
            listing_id   = escrow.listing_id,
            redirect_url = redirect_url,
        )

        if result['success']:
            escrow.mpesa_reference = result.get('tx_ref', '')
            escrow.save()
            return Response({'payment_link': result['payment_link'], 'tx_ref': result.get('tx_ref')})

        if result.get('simulated'):
            return Response({'message': 'flutterwave not configured. payment simulated for development.'})

        return Response({'error': result.get('error')}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def webhook(self, request):
        # receives flutterwave payment notifications
        signature = request.headers.get('verif-hash', '')
        from .flutterwave import verify_webhook, verify_payment
        if not verify_webhook(request.body, signature):
            return Response({'error': 'invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)

        data           = request.data
        tx_id          = data.get('id')
        tx_ref         = data.get('txRef') or data.get('tx_ref', '')
        event          = data.get('event', '')

        if event == 'charge.completed':
            verification = verify_payment(tx_id)
            if verification.get('paid'):
                escrow = EscrowTransaction.objects.filter(mpesa_reference=tx_ref).first()
                if escrow:
                    escrow.status = 'held'
                    escrow.save()

        return Response({'status': 'ok'})
