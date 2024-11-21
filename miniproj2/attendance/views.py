from rest_framework import generics, permissions, serializers
from .models import  Attendance, AttendanceWindow
from .serializers import  AttendanceSerializer, AttendanceWindowSerializer
from .permissions import CanManageAttendance
from rest_framework.viewsets import ModelViewSet
from courses.models import Enrollment
from students.models import Student
from users.permissions import IsTeacher, IsAdmin, IsStudent
from rest_framework.exceptions import ValidationError

from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger("custom")

class AttendanceViewSet(ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsTeacher() or IsAdmin()]
        elif self.action in ["retrieve"]:
            return [IsAuthenticated(), IsStudent() or IsTeacher() or IsAdmin()]
        elif self.action in ["list"]:
            return [IsAuthenticated(), IsTeacher() or IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == "student":
            return Attendance.objects.filter(user=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        attendance = serializer.save()
        logger.info(
            f"Attendance marked: Student {attendance.student.user.username} - "
            f"Course {attendance.course.name} - Status {attendance.status}"
        )


class AttendanceWindowCreateView(generics.CreateAPIView):
    queryset = AttendanceWindow.objects.all()
    serializer_class = AttendanceWindowSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher | IsAdmin]

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

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != 'student' | user.role != "admin":
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
