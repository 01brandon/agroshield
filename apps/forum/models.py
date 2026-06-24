from django.db import models
from django.conf import settings

class Post(models.Model):
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title      = models.CharField(max_length=300)
    body       = models.TextField()
    photo_url  = models.URLField(blank=True)
    crop_tag   = models.CharField(max_length=100, blank=True)
    upvotes    = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Reply(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body       = models.TextField()
    is_expert  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
