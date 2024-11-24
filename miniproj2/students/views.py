from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from pagination.pagination import CustomPagination
from .models import Student
from .serializers import StudentSerializer, GetStudentSerializer
from .tasks import invalidate_student_cache, refresh_student_cache
import logging

logger = logging.getLogger("custom")


class StudentListView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = GetStudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    ordering_fields = ['registration_date', 'name']
    ordering = ['registration_date']

    @extend_schema(
        description="Retrieve a list of students",
        responses={200: GetStudentSerializer(many=True), 400: "Bad Request"},
        parameters=[
            OpenApiParameter('name', type=str, description="Filter students by name"),
            OpenApiParameter('registration_date', type=str, description="Filter students by registration date"),
            OpenApiParameter('ordering', type=str, description="Order by fields, e.g., 'registration_date' or 'name'")
        ]
    )
    def get_queryset(self):
        user = self.request.user
        cache_key = "student_list_all"

        student_list = cache.get(cache_key)
        if student_list is None:
            logger.info(f"Cache miss for student list: {cache_key}")
            if user.role == "student":
                student_list = Student.objects.filter(user=user)
            elif user.role == "admin":
                student_list = Student.objects.all()
            else:
                student_list = Student.objects.none()
            cache.set(cache_key, student_list, timeout=60 * 15)
        else:
            logger.info(f"Cache hit for student list: {cache_key}")

        return student_list


class StudentProfileView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = GetStudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Retrieve a student's profile by ID",
        responses={200: GetStudentSerializer, 404: "Not Found", 400: "Bad Request"},
        parameters=[
            OpenApiParameter('id', type=int, description="The ID of the student to retrieve")
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        student_id = kwargs["pk"]
        cache_key = f"student_profile_{student_id}"

        student = cache.get(cache_key)
        if not student:
            logger.info(f"Cache miss for student profile: {student_id}")
            student = self.get_object()
            cache.set(cache_key, student, timeout=3600)
        else:
            logger.info(f"Cache hit for student profile: {student_id}")

        serializer = self.get_serializer(student)
        return Response(serializer.data)


class StudentUpdateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Update a student's profile by ID",
        request=StudentSerializer,
        responses={200: StudentSerializer, 400: "Validation Error", 404: "Not Found"},
        parameters=[
            OpenApiParameter('id', type=int, description="The ID of the student to update")
        ]
    )
    def get_object(self):
        student = super().get_object()
        if self.request.user != student.user and self.request.user.role != 'admin':
            raise PermissionDenied("You do not have permission to update this record.")
        return student

    def perform_update(self, serializer):
        instance = serializer.save()

        profile_cache_key = f"student_profile_{instance.id}"
        list_cache_key = f"student_list_{instance.user.id}"

        invalidate_student_cache(instance.id)
        logger.info(f"Cache invalidated for student profile: {profile_cache_key}")

        refresh_student_cache(instance.id)
        logger.info(f"Cache refreshed for student profile: {profile_cache_key}")

        cache.delete(list_cache_key)
        logger.info(f"Cache invalidated for student list: {list_cache_key}")

        updated_student_list = Student.objects.all()
        cache.set(list_cache_key, updated_student_list, timeout=60)  # Shorter timeout for debugging
        logger.info(f"Cache refreshed for global student list: {list_cache_key}")
