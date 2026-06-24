from rest_framework.routers import DefaultRouter
from .views import SoilReadingViewSet
router = DefaultRouter()
router.register('', SoilReadingViewSet, basename='soil')
urlpatterns = router.urls
