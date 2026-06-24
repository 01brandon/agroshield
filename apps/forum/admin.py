from django.contrib import admin
from .models import Post, Reply

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title','author','crop_tag','upvotes','created_at']

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ['post','author','is_expert','created_at']
