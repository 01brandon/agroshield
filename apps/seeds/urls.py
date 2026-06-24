from rest_framework.routers import DefaultRouter
from .views import SeedProductViewSet
router = DefaultRouter()
router.register('', SeedProductViewSet, basename='seed')
urlpatterns = router.urls
