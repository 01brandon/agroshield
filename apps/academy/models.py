from django.db import models
from django.conf import settings

class Course(models.Model):
    title       = models.CharField(max_length=300)
    description = models.TextField()
    video_url   = models.URLField(blank=True)
    thumbnail   = models.URLField(blank=True)
    duration    = models.IntegerField(help_text='minutes')
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course       = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_pct = models.IntegerField(default=0)
    completed    = models.BooleanField(default=False)
    enrolled_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user','course']

    def __str__(self):
        return f'{self.user.email} - {self.course.title}'
