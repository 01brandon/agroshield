from rest_framework.routers import DefaultRouter
from .views import NDVIReadingViewSet
router = DefaultRouter()
router.register('', NDVIReadingViewSet, basename='ndvi')
urlpatterns = router.urls
