from users.models import User 
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from courses.models import Course

class MostActiveUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Count all API requests made by the user, including course accesses
        active_users = User.objects.annotate(
            api_requests_count=Count('apirequestlog')  # Count all requests
        ).order_by('-api_requests_count')[:10]  # Order by total API requests in descending order

        user_data = [
            {"username": user.username, "api_requests_count": user.api_requests_count}
            for user in active_users
        ]
        return Response(user_data)

class MostPopularCoursesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        popular_courses = Course.objects.annotate(
            enrollment_count=Count('enrollments') 
        ).order_by('-enrollment_count')[:10]

        course_data = [
            {"course_name": course.name, "enrollment_count": course.enrollment_count}
            for course in popular_courses
        ]
        return Response(course_data)