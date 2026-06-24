from rest_framework.routers import DefaultRouter
from .views import FoodSecurityAlertViewSet
router = DefaultRouter()
router.register('', FoodSecurityAlertViewSet, basename='alert')
urlpatterns = router.urls
