from django.db import models
from courses.models import Course, Enrollment
from students.models import Student

'''class AttendanceWindow(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendance_windows")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_open = models.BooleanField(default=True)
    
    def close_window(self):
        self.is_open = False
        self.save()

        # Mark absent for students who didn't mark attendance
        enrolled_students = Enrollment.objects.filter(course=self.course).values_list('student', flat=True)
        for student_id in enrolled_students:
            Attendance.objects.get_or_create(
                student_id=student_id,
                course=self.course,
                date=self.date,
                defaults={"status": "absent", "marked_on_time": False},
            )

    def __str__(self):
        return f"{self.course.name} - {self.date} ({'Open' if self.is_open else 'Closed'})"'''

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        #('late', 'Late'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendance")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_on_time = models.BooleanField(default=True) 

    class Meta:
        unique_together = ('student', 'course', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.course.name} on {self.date}: {self.status}"
    
