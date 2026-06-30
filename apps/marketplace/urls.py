from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BidViewSet, EscrowViewSet

router = DefaultRouter()
router.register('listings',  ListingViewSet,           basename='listing')
router.register('bids',      BidViewSet,               basename='bid')
router.register('escrow',    EscrowViewSet,            basename='escrow')
urlpatterns = router.urls
