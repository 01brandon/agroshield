from rest_framework.routers import DefaultRouter
from .views import CropScanViewSet
router = DefaultRouter()
router.register('', CropScanViewSet, basename='cropscan')
urlpatterns = router.urls
