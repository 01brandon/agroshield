from rest_framework.routers import DefaultRouter
from .views import CarbonActivityViewSet
router = DefaultRouter()
router.register('', CarbonActivityViewSet, basename='carbon')
urlpatterns = router.urls
