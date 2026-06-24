from django.db import models
from django.conf import settings

class Cooperative(models.Model):
    name        = models.CharField(max_length=200)
    admin       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_coops')
    members     = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='cooperatives', blank=True)
    description = models.TextField(blank=True)
    location    = models.CharField(max_length=200, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
