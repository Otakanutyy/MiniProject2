from rest_framework import serializers
from .models import Attendance, Student, Course , AttendanceWindow
from students.serializers import StudentSerializer
from courses.serializers import CourseSerializer

class AttendanceWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceWindow
        fields = ['id', 'course', 'date', 'timer', 'is_open']
        read_only_fields = ['is_open']


class NextAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'course', 'date', 'status', 'marked_on_time']
        read_only_fields = ['marked_on_time', 'student', 'course', 'date']  # These are read-only for update

    def create(self, validated_data):
        user = self.context['request'].user
        student = user.student_profile

        course = validated_data.get('course')
        date = validated_data.get('date')

        #window = AttendanceWindow.objects.filter(course=course, date=date, is_open=True).first()
        #if not window:
        #    raise serializers.ValidationError({"detail": "Attendance is not open for this course."})

        # Mark attendance
        validated_data['student'] = student
        validated_data['status'] = 'present'
        validated_data['marked_on_time'] = True
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('course', None)
        validated_data.pop('date', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ["id", "student", "course", "date", "status", "marked_on_time"]
        read_only_fields = ["marked_on_time", "status", "student"]