from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from .models import APIRequestLog, CourseAccessLog
from drf_spectacular.utils import extend_schema
from users.models import User
from .models import ActiveUser

class MostActiveUsersView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get the most active users based on the number of API requests",
        responses={200: "List of most active users"},
    )
    def get(self, request, *args, **kwargs):
        active_users = ActiveUser.objects.filter(user__is_superuser=False).order_by('-api_calls')[:10]
        data = [{"username": user.user.username, "api_calls": user.api_calls} for user in active_users]

        if not data:
            return Response({"message": "No active users found."}, status=200)

        return Response(data)


class MostPopularCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get the most popular courses based on the number of accesses",
        responses={200: "List of most popular courses"},
    )
    def get(self, request, *args, **kwargs):
        popular_courses = CourseAccessLog.objects.values('course_id') \
            .annotate(access_count=Count('course_id')) \
            .order_by('-access_count')[:10]
        
        data = [{"course_id": course['course_id'], "access_count": course['access_count']} for course in popular_courses]
        return Response(data)

