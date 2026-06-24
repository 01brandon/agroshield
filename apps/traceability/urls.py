from rest_framework.routers import DefaultRouter
from .views import BatchViewSet, EntryViewSet
router = DefaultRouter()
router.register('batches', BatchViewSet, basename='batch')
router.register('entries', EntryViewSet, basename='entry')
urlpatterns = router.urls
