from rest_framework import viewsets, permissions
from .models import Post, Reply
from .serializers import PostSerializer, ReplySerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset           = Post.objects.all()
    serializer_class   = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReplyViewSet(viewsets.ModelViewSet):
    queryset           = Reply.objects.all()
    serializer_class   = ReplySerializer
    permission_classes = [permissions.IsAuthenticated]
