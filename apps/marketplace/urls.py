from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BidViewSet, EscrowViewSet, FlutterwavePaymentViewSet

router = DefaultRouter()
router.register('listings',  ListingViewSet,           basename='listing')
router.register('bids',      BidViewSet,               basename='bid')
router.register('escrow',    EscrowViewSet,            basename='escrow')
router.register('payments',  FlutterwavePaymentViewSet, basename='flutterwave')
urlpatterns = router.urls
