from django.db import models
from django.conf import settings
from django.db.models import Count
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


class MostActiveUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        active_users = User.objects.annotate(
            courses_accessed=Count('courseaccesslog'),
            courses_enrolled=Count('enrollmentlog')
        ).order_by('-courses_accessed', '-courses_enrolled')[:10] 

        user_data = [
            {"username": user.username, "courses_accessed": user.courses_accessed, "courses_enrolled": user.courses_enrolled}
            for user in active_users
        ]
        return Response(user_data)
    
class CourseAccessLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} accessed {self.course}"

class EnrollmentLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} enrolled in {self.course}"

class APIRequestLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.user.username} to {self.endpoint} at {self.timestamp}"
