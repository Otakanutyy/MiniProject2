from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q
from .models import Grade
from .serializers import GradeSerializer
from .tasks import send_grade_update_report
from .permissions import IsInstructorOrAdmin
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from users.models import User

import logging

logger = logging.getLogger("custom")

class GradeViewSet(ModelViewSet):
    """
    ViewSet for managing grade records.
    - Students can view only their grades.
    - Teachers and admins have full access.
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Retrieve all grades (Students see only their grades)",
        responses={200: GradeSerializer(many=True), 400: "Bad Request"},
        parameters=[
            OpenApiParameter('student', type=int, description="Filter grades by student ID"),
            OpenApiParameter('course', type=int, description="Filter grades by course ID"),
            OpenApiParameter('ordering', type=str, description="Order by fields, e.g., 'grade', 'course'")
        ]
    )
    def get_queryset(self):
        user = self.request.user
        if user.role == "student":
            # Students can only view their own grades
            return Grade.objects.filter(student__user=user)
        elif user.role == "teacher":
            # Teachers can view grades of their courses
            return Grade.objects.filter(course__instructor=user)
        return super().get_queryset()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsInstructorOrAdmin()]
        elif self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == "teacher":
            serializer.save(teacher=user)
        elif user.role == "admin":
            course = serializer.validated_data.get('course')
            if course:
                teacher = course.instructor
                if teacher:
                    serializer.save(teacher=teacher)
                else:
                    raise serializers.ValidationError({"teacher": "The course does not have an instructor."})
            else:
                raise serializers.ValidationError({"course": "A course must be provided."})

        grade = serializer.instance
        logger.info(
            f"Grade created: Student {grade.student.user.username} - "
            f"Course {grade.course.name} - Grade {grade.grade} - "
            f"Teacher {grade.teacher.username}" 
        )
        send_grade_update_report.apply_async(args=[grade.id])

    

    def perform_update(self, serializer):
        grade = serializer.save()
        logger.info(
            f"Grade updated: Student {grade.student.user.username} - "
            f"Course {grade.course.name} - Grade {grade.grade}"
        )
        send_grade_update_report.apply_async(args=[grade.id])
