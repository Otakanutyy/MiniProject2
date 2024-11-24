from rest_framework import generics, permissions, serializers
from .models import Attendance, AttendanceWindow
from .serializers import AttendanceSerializer, AttendanceWindowSerializer
from .permissions import CanManageAttendance
from rest_framework.viewsets import ModelViewSet
from courses.models import Enrollment
from students.models import Student
from users.permissions import IsTeacher, IsAdmin, IsStudent
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

import logging

logger = logging.getLogger("custom")


class AttendanceViewSet(ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Retrieve a list of attendance records (Students see only their attendance)",
        responses={200: AttendanceSerializer(many=True), 400: "Validation Error"},
        parameters=[
            OpenApiParameter('course', type=str, description="Filter attendance by course (e.g., 'Math 101')"),
            OpenApiParameter('status', type=str, description="Filter attendance by status (e.g., 'present', 'absent')"),
            OpenApiParameter('ordering', type=str, description="Order by field(s), e.g., 'date', 'course', 'status'")
        ]
    )
    def get_queryset(self):
        user = self.request.user
        if user.role == "student":
            # Students can only view their own attendance
            return Attendance.objects.filter(student__user=user)
        return super().get_queryset()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            # Only teachers and admins can modify attendance records
            return [IsAuthenticated(), IsTeacher() or IsAdmin()]
        elif self.action in ["list", "retrieve"]:
            # All authenticated users can view attendance, but students see only their own
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    @extend_schema(
        description="Retrieve an attendance record by ID",
        responses={200: AttendanceSerializer, 404: "Not Found"}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Create a new attendance record",
        request=AttendanceSerializer,
        responses={201: AttendanceSerializer, 400: "Validation Error"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Update an attendance record by ID",
        request=AttendanceSerializer,
        responses={200: AttendanceSerializer, 400: "Validation Error"}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Delete an attendance record by ID",
        responses={204: "No Content", 404: "Not Found"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        attendance = serializer.save()
        logger.info(
            f"Attendance marked: Student {attendance.student.user.username} - "
            f"Course {attendance.course.name} - Status {attendance.status}"
        )

    def perform_update(self, serializer):
        user = self.request.user
        if user.role not in ['teacher', 'admin']:
            raise serializers.ValidationError({"detail": "You do not have permission to update attendance."})

        attendance = serializer.save()
        logger.info(
            f"Attendance updated: Student {attendance.student.user.username} - "
            f"Course {attendance.course.name} - New Status {attendance.status}"
        )

class AttendanceWindowCreateView(generics.CreateAPIView):
    queryset = AttendanceWindow.objects.all()
    serializer_class = AttendanceWindowSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher | IsAdmin]

    @extend_schema(
        description="Open a new attendance window for a course",
        request=AttendanceWindowSerializer,
        responses={201: AttendanceWindowSerializer, 400: "Validation Error"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        course = serializer.validated_data['course']
        if user.role == 'teacher' and course.instructor != user:
            raise serializers.ValidationError(
                {"detail": "You can only open attendance for your own courses."}
            )

        serializer.save()


class AttendanceMarkView(generics.CreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Mark attendance for a course",
        request=AttendanceSerializer,
        responses={
            201: ("Attendance marked successfully", AttendanceSerializer),
            400: ("Validation error")
        }
    )

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != 'student':
            raise ValidationError({"detail": "Only students can mark attendance."})

        try:
            student_profile = user.student_profile
        except Student.DoesNotExist:
            raise ValidationError({"detail": "Student profile not found."})

        course = serializer.validated_data['course']
        date = serializer.validated_data['date']

        if not course.enrollments.filter(student=student_profile).exists():
            raise ValidationError({"detail": "You are not enrolled in this course."})

        attendance_window = AttendanceWindow.objects.filter(
            course=course, is_open=True
        ).first()

        if not attendance_window:
            raise ValidationError({"detail": "Attendance is not open for this course."})

        if attendance_window.date != date:
            raise ValidationError({"detail": "Attendance is only open for today."})

        serializer.save(student=student_profile, status="present", marked_on_time=True)
