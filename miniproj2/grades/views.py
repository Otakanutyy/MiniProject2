from rest_framework.viewsets import ModelViewSet

from users.permissions import IsTeacher, IsAdmin, IsStudent
from .models import Grade
from .serializers import GradeSerializer
from rest_framework.permissions import IsAuthenticated
from .tasks import send_grade_update_report

import logging

logger = logging.getLogger("custom")

class GradeViewSet(ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

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
            return Grade.objects.filter(student__user=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        grade = serializer.save()
        logger.info(
            f"Grade created: Student {grade.student.user.username} - "
            f"Course {grade.course.name} - Grade {grade.grade}"
        )
        
        send_grade_update_report.apply_async(args=[grade.id])

    def perform_update(self, serializer):
        grade = serializer.save()
        logger.info(
            f"Grade updated: Student {grade.student.user.username} - "
            f"Course {grade.course.name} - Grade {grade.grade}"
        )
        
        send_grade_update_report.apply_async(args=[grade.id])