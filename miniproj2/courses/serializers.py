from rest_framework import serializers
from .models import Enrollment, Course

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_on']
        read_only_fields = ['enrolled_on']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'instructor']
        extra_kwargs = {'instructor': {'required': False}}  

    def create(self, validated_data):
        user = self.context['request'].user
        if 'instructor' not in validated_data:
            validated_data['instructor'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'instructor' in validated_data:
            if self.context['request'].user.role != 'admin':
                validated_data.pop('instructor', None)
        return super().update(instance, validated_data)

