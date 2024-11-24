from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class APIRequestLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    endpoint = models.CharField(max_length=255)

    def __str__(self):
        return f"Request by {self.user.username} at {self.timestamp} for {self.endpoint}"

class PopularCourse(models.Model):
    course_id = models.IntegerField(unique=True)
    views = models.IntegerField(default=0)


class CourseAccessLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user.username} accessed course {self.course_id} at {self.timestamp}"

class ActiveUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    api_calls = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.api_calls} API calls"