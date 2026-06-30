from rest_framework.routers import DefaultRouter
from .views import PostViewSet, ReplyViewSet
router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('replies', ReplyViewSet, basename='reply')
urlpatterns = router.urls
