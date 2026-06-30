from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post, Reply
from .serializers import PostSerializer, ReplySerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def ai_answer(self, request, pk=None):
        post = self.get_object()
        from .ai_copilot import get_ai_response
        result = get_ai_response(question=f'{post.title}\n\n{post.body}', crop_tag=post.crop_tag)
        Reply.objects.create(post=post, author=request.user, body=f'[ai co-pilot]\n\n{result["response"]}', is_expert=True)
        return Response({'response': result['response']})

    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        post = self.get_object()
        post.upvotes += 1
        post.save()
        return Response({'upvotes': post.upvotes})

class ReplyViewSet(viewsets.ModelViewSet):
    serializer_class = ReplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Reply.objects.all()
        post_id = self.request.query_params.get('post')
        if post_id:
            qs = qs.filter(post_id=post_id)
        return qs
