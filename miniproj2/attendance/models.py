from django.db import models
from courses.models import Course, Enrollment
from students.models import Student
from datetime import timedelta
from django.utils.timezone import now

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
    
class AttendanceWindow(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendance_windows")
    date = models.DateField(auto_now_add=True)
    timer = models.PositiveIntegerField() 
    is_open = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None 
        super().save(*args, **kwargs)

        if is_new and self.is_open:
            from .tasks import close_window_task
            close_window_task.apply_async(
                args=[self.id],
                eta=now() + timedelta(minutes=self.timer)
            )

    def close_window(self):
        if self.is_open:
            self.is_open = False
            self.save()

            enrolled_students = Enrollment.objects.filter(course=self.course).values_list('student', flat=True)
            for student_id in enrolled_students:
                Attendance.objects.get_or_create(
                    student_id=student_id,
                    course=self.course,
                    date=self.date,
                    defaults={"status": "absent", "marked_on_time": False},
                )

    def __str__(self):
        return f"{self.course.name} - {self.date} ({'Open' if self.is_open else 'Closed'})"