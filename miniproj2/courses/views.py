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

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Enrollment
from .serializers import EnrollmentSerializer
from .permissions import CanManageEnrollments
from users.models import User
import logging


logger = logging.getLogger("custom")

class EnrollmentListCreateView(generics.ListCreateAPIView):
    serializer_class = EnrollmentSerializer

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

        logger.info(
            f"Student {enrollment.student.user.username} enrolled in course {enrollment.course.name}"
        )


class CourseDetailUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageCourses]


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageCourses]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [permissions.IsAuthenticated(), CanManageCourses()]

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
            # Assign teacher as instructor
            serializer.save(instructor=user)
        elif user.role == 'admin':
            # Admins must specify an instructor
            instructor_pk = self.request.data.get('instructor')
            if instructor_pk:
                try:
                    instructor = User.objects.get(pk=instructor_pk, role='teacher')
                    serializer.save(instructor=instructor)
                except User.DoesNotExist:
                    raise serializers.ValidationError({"instructor": "The specified instructor does not exist or is not a teacher."})
            else:
                raise serializers.ValidationError({"instructor": "Admins must provide an instructor."})


