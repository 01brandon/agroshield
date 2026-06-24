from rest_framework.routers import DefaultRouter
from .views import EquipmentListingViewSet, EquipmentBookingViewSet
router = DefaultRouter()
router.register('listings', EquipmentListingViewSet, basename='equipment-listing')
router.register('bookings', EquipmentBookingViewSet, basename='equipment-booking')
urlpatterns = router.urls
