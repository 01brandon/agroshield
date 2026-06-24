from rest_framework import serializers
from .models import Post, Reply

class ReplySerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.full_name')

    class Meta:
        model  = Reply
        fields = '__all__'
        read_only_fields = ['author','created_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.full_name')
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model  = Post
        fields = '__all__'
        read_only_fields = ['author','upvotes','created_at']

    def get_reply_count(self, obj):
        return obj.replies.count()

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
