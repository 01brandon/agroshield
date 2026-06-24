from rest_framework.routers import DefaultRouter
from .views import DroneOperatorViewSet, DroneBookingViewSet
router = DefaultRouter()
router.register('operators', DroneOperatorViewSet, basename='drone-operator')
router.register('bookings',  DroneBookingViewSet,  basename='drone-booking')
urlpatterns = router.urls
