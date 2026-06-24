from rest_framework.routers import DefaultRouter
from .views import AnimalViewSet, HealthRecordViewSet
router = DefaultRouter()
router.register('animals', AnimalViewSet,       basename='animal')
router.register('health',  HealthRecordViewSet, basename='health')
urlpatterns = router.urls
