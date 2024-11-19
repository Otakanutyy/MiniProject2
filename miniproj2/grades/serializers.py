from rest_framework import serializers

from users.serializers import UserSerializer
from courses.serializers import CourseSerializer
from students.serializers import StudentSerializer

from .models import Grade


class GradeSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Grade
        fields = ["id", "student", "course", "grade", "teacher", "date"]

    '''def validate(self, data):
        user = self.context['request'].user
        
        # teacher is instructor
        if user.role == 'teacher' and data['course'].instructor != user:
            raise serializers.ValidationError("You can only assign grades for courses you instruct.")
        
        # student enrolled
        if not data['course'].enrollments.filter(student=data['student']).exists():
            raise serializers.ValidationError("The student is not enrolled in this course.")

        return data'''
