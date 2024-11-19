from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Student
from .serializers import StudentSerializer, GetStudentSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
import logging
from rest_framework.response import Response

logger = logging.getLogger("custom")
class StudentListView(generics.ListAPIView):
    serializer_class = GetStudentSerializer
    permission_classes = [IsAuthenticated]
    #pagination_class = CustomPagination  # Add pagination if needed
    
    def get_queryset(self):
        user = self.request.user
        cache_key = f"student_list_{user.id}"

        # Try to fetch cached student list
        student_list = cache.get(cache_key)

        if student_list is None:
            if user.role == "student":
                student_list = Student.objects.filter(user=user)
            elif user.role == "admin":
                student_list = Student.objects.all()
            else:
                student_list = Student.objects.none()

            # Cache the queryset for 15 minutes
            cache.set(cache_key, student_list, timeout=60*15)

        return student_list

class StudentProfileView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = GetStudentSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        student_id = kwargs["pk"]
        cache_key = f"student_profile_{student_id}"

        # Check if the student profile is in the cache
        student = cache.get(cache_key)

        if student:
            logger.info(f"Cache hit for student profile: {student_id}")
        else:
            logger.info(f"Cache miss for student profile: {student_id}")
            student = self.get_object()  # Fetch from database if not in cache
            # Cache the student profile for 1 hour
            cache.set(cache_key, student, timeout=3600)

        # Serialize and return the cached student profile
        serializer = self.get_serializer(student)
        return Response(serializer.data)

class StudentUpdateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        student = super().get_object()

        # Ensure the user is authorized to update the student profile
        if self.request.user != student.user and self.request.user.role != 'admin':
            raise PermissionDenied("You do not have permission to update this record.")
        
        return student

    def perform_update(self, serializer):
        instance = serializer.save()

        # Invalidate the cache after updating the profile
        cache_key = f"student_profile_{instance.id}"
        cache.delete(cache_key)
        logger.info(f"Cache invalidated for student profile: {instance.id}")