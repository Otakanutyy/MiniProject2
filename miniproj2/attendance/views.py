from rest_framework import generics, permissions, serializers
from .models import  Attendance
from .serializers import  AttendanceSerializer
from .permissions import CanManageAttendance
from rest_framework.viewsets import ModelViewSet
from courses.models import Enrollment
from students.models import Student
from users.permissions import IsTeacher, IsAdmin, IsStudent

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





'''class AttendanceWindowListCreateView(generics.ListCreateAPIView):
    queryset = AttendanceWindow.objects.all()
    serializer_class = AttendanceWindowSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageAttendance]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return AttendanceWindow.objects.filter(course__instructor=user)
        return AttendanceWindow.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        course = serializer.validated_data['course']

        # Ensure teachers can only open windows for their courses
        if user.role == 'teacher' and course.instructor != user:
            raise serializers.ValidationError({"detail": "You can only open attendance for your own courses."})

        serializer.save()


class StudentAttendanceCreateView(generics.CreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user  # This is the logged-in user
        student_profile = user.student_profile  # Get the Student instance via the related_name
        course = serializer.validated_data['course']
        date = serializer.validated_data['date']

        # Check if the student is enrolled in the course
        if not course.enrollments.filter(student=student_profile).exists():
            raise serializers.ValidationError({"detail": "You are not enrolled in this course."})

        # Check if an attendance window is open
        attendance_window = AttendanceWindow.objects.filter(
            course=course, date=date, is_open=True
        ).first()
        if not attendance_window:
            raise serializers.ValidationError({"detail": "Attendance is not open for this course."})

        # Ensure you're passing the Student instance, not a string or identifier
        serializer.save(student=student_profile)




def mark_absent_after_window():
    current_time = now()
    closed_windows = AttendanceWindow.objects.filter(end_time__lte=current_time, is_open=True)
    
    for window in closed_windows:
        window.is_open = False
        window.save()

        # Get all enrolled students for the course
        enrolled_students = Enrollment.objects.filter(course=window.course).values_list('student', flat=True)

        # Mark absent for students who did not mark attendance
        for student_id in enrolled_students:
            Attendance.objects.get_or_create(
                student_id=student_id,
                course=window.course,
                date=window.date,
                defaults={"status": "absent", "marked_on_time": False},
            )


class AttendanceUpdateView(generics.UpdateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageAttendance]

    def perform_update(self, serializer):
        # Get the attendance object
        attendance = self.get_object()

        # Check if the attendance window is closed
        attendance_window = AttendanceWindow.objects.filter(
            course=attendance.course, date=attendance.date
        ).first()

        if attendance_window and not attendance_window.is_open:
            # If the window is closed, mark the attendance as "late"
            serializer.save(status="late", marked_on_time=False)
        else:
            # Otherwise, save the attendance as normal
            serializer.save()



#getters
class AttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            # Admin can see all attendance records
            return Attendance.objects.all()
        
        elif user.role == 'teacher':
            # Teacher can see attendance for their courses (students enrolled in their courses)
            return Attendance.objects.filter(course__instructor=user)
        
        elif user.role == 'student':
            # Ensure we're querying with the correct student instance
            student = Student.objects.get(user=user)  # Fetch the actual Student instance related to the user
            return Attendance.objects.filter(student=student)

        return Attendance.objects.none()  # Default to empty queryset if role is unknown
'''