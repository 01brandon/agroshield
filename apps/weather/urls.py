from rest_framework.routers import DefaultRouter
from .views import WeatherAlertViewSet, WeatherReadingViewSet

router = DefaultRouter()
router.register('alerts',   WeatherAlertViewSet,   basename='weather-alert')
router.register('readings', WeatherReadingViewSet, basename='weather-reading')
urlpatterns = router.urls
