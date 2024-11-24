from rest_framework import serializers
from .models import Grade
from courses.models import Course
from students.models import Student
from users.models import User

class GradeSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='teacher'), required=False)

    class Meta:
        model = Grade
        fields = ["id", "student", "course", "grade", "teacher", "date"]
