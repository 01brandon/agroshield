from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Post, Reply
from .serializers import PostSerializer, ReplySerializer

@extend_schema_view(
    list=extend_schema(tags=['forum'], summary='List all forum posts', description='Returns posts with reply_count and upvote totals.'),
    create=extend_schema(tags=['forum'], summary='Create a new forum post'),
    retrieve=extend_schema(tags=['forum'], summary='Retrieve a specific post'),
    destroy=extend_schema(tags=['forum'], summary='Delete a post (owner only)'),
)
class PostViewSet(viewsets.ModelViewSet):
    queryset           = Post.objects.all()
    serializer_class   = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['forum'],
        summary='Get an AI co-pilot answer for this post',
        description='Sends the post content to Google Gemini and saves the response as an expert reply. No request body needed.',
        responses={200: {'type': 'object', 'properties': {'response': {'type': 'string'}}}}
    )
    @action(detail=True, methods=['post'])
    def ai_answer(self, request, pk=None):
        post = self.get_object()
        from .ai_copilot import get_ai_response
        result = get_ai_response(question=f'{post.title}\n\n{post.body}', crop_tag=post.crop_tag)
        Reply.objects.create(post=post, author=request.user, body=f'[ai co-pilot]\n\n{result["response"]}', is_expert=True)
        return Response({'response': result['response']})

    @extend_schema(tags=['forum'], summary='Upvote a post', responses={200: {'type': 'object', 'properties': {'upvotes': {'type': 'integer'}}}})
    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        post = self.get_object()
        post.upvotes += 1
        post.save()
        return Response({'upvotes': post.upvotes})


@extend_schema_view(
    list=extend_schema(tags=['forum'], summary='List replies. Filter by post using ?post={id}'),
    create=extend_schema(tags=['forum'], summary='Add a reply to a forum post'),
)
class ReplyViewSet(viewsets.ModelViewSet):
    serializer_class   = ReplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs      = Reply.objects.all()
        post_id = self.request.query_params.get('post')
        if post_id:
            qs = qs.filter(post_id=post_id)
        return qs
