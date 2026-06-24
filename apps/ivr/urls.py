from rest_framework.routers import DefaultRouter
from .views import VoiceInteractionViewSet
router = DefaultRouter()
router.register('', VoiceInteractionViewSet, basename='ivr')
urlpatterns = router.urls
