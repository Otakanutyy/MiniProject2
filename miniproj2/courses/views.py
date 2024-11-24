from rest_framework import generics, permissions
from .models import Enrollment, Course
from .serializers import EnrollmentSerializer, CourseSerializer
from .permissions import CanManageEnrollments, CanManageCourses
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from .models import Course
from rest_framework.exceptions import PermissionDenied
from django.core.cache import cache
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Enrollment
from .serializers import EnrollmentSerializer
from .permissions import CanManageEnrollments
from users.models import User

from drf_spectacular.utils import extend_schema, OpenApiParameter
import logging


from pagination.pagination import CustomPagination

logger = logging.getLogger("custom")

from analytics.models import CourseAccessLog, EnrollmentLog
from django.utils.timezone import make_aware
from datetime import datetime

class EnrollmentListCreateView(generics.ListCreateAPIView):
    serializer_class = EnrollmentSerializer
    pagination_class = CustomPagination

    @extend_schema(
    description="Retrieve a list of enrollments or create a new enrollment",
    responses={200: EnrollmentSerializer(many=True), 201: EnrollmentSerializer, 400: "Validation Error"},
    parameters=[
        OpenApiParameter('student', type=int, description="Filter by student ID"),
        OpenApiParameter('course', type=int, description="Filter by course ID"),
        OpenApiParameter('ordering', type=str, description="Order by field(s), e.g., 'registration_date'")
    ]
)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()] 
        return [IsAuthenticated(), CanManageEnrollments()] 

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Enrollment.objects.all()  
        elif user.role == 'teacher':
            return Enrollment.objects.filter(course__instructor=user)
        elif user.role == 'student':
            return Enrollment.objects.filter(student__user=user)
        return Enrollment.objects.none()

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        user = self.request.user
      
        if user.role == 'teacher' and course.instructor != user:
            raise PermissionDenied("You can only manage enrollments for your courses.")
     
        if user.role == 'admin':
            enrollment = serializer.save()  
        else:
            if user.role == 'student':
                raise PermissionDenied("Students cannot create enrollments.")
            enrollment = serializer.save()

        EnrollmentLog.objects.create(user=user, course=course)

        logger.info(
            f"Student {enrollment.student.user.username} enrolled in course {enrollment.course.name}"
        )


class CourseDetailUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageCourses]

    @extend_schema(
        description="Retrieve course details by ID",
        responses={200: CourseSerializer, 404: "Not Found"},
        parameters=[
            #OpenApiParameter('id', type=int, description="The ID of the course to retrieve or update")
        ]
    )
    def get(self, request, *args, **kwargs):
        course = self.get_object()
        CourseAccessLog.objects.create(user=request.user, course=course)
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Update course details by ID",
        request=CourseSerializer,
        responses={200: CourseSerializer, 400: "Validation Error"},
        parameters=[
            OpenApiParameter('id', type=int, description="The ID of the course to retrieve or update")
        ]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageCourses]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("name",)

    @extend_schema(
        description="Retrieve a list of courses",
        responses={200: CourseSerializer(many=True)},
        parameters=[
            OpenApiParameter('name', type=str, description="Filter courses by name"),
            OpenApiParameter('ordering', type=str, description="Order by field(s), e.g., 'name', 'instructor'")
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Create a new course",
        request=CourseSerializer,
        responses={201: CourseSerializer, 400: "Validation Error"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [permissions.IsAuthenticated(), CanManageCourses()]

    @extend_schema(
        description="Retrieve a cached list of courses",
        responses={200: CourseSerializer(many=True)},
        parameters=[
            OpenApiParameter('role', type=str, description="Filter courses by user role ('teacher', 'student')")
        ]
    )
    @action(detail=False, methods=["get"])
    def cached_list(self, request):
        user = request.user
        cache_key = f"courses_list_{user.id}"
        courses = cache.get(cache_key)

        if not courses:
            if user.role == "teacher":
                courses = Course.objects.filter(instructor=user)
            elif user.role == "student":
                courses = Course.objects.filter(enrollment__student__user=user)
            else:
                courses = Course.objects.all()

            cache.set(cache_key, courses, timeout=3600)

        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == 'teacher':
            serializer.save(instructor=user)
        elif user.role == 'admin':
            instructor_pk = self.request.data.get('instructor')
            if instructor_pk:
                try:
                    instructor = User.objects.get(pk=instructor_pk, role='teacher')
                    serializer.save(instructor=instructor)
                except User.DoesNotExist:
                    raise serializers.ValidationError({"instructor": "The specified instructor does not exist or is not a teacher."})
            else:
                raise serializers.ValidationError({"instructor": "Admins must provide an instructor."})
        self.invalidate_course_list_cache(user)

    def invalidate_course_list_cache(self, user):
        cache_key = f"courses_list_{user.id}"
        cache.delete(cache_key)
        logger.info(f"Cache invalidated for course list: {cache_key}")

