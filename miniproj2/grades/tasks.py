from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Grade
import logging

logger = logging.getLogger("custom")
@shared_task
def send_grade_update_report(grade_id):
    try:
        grade = Grade.objects.get(id=grade_id)
        student = grade.student
        course = grade.course

        subject = f"Grade Update for {course.name}"
        message = f"""
        Dear {student.user.username},

        Your grade for the course {course.name} has been updated. 
        New Grade: {grade.grade}
        Date: {grade.date}
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [student.user.email],
        )
        logger.info(f"Grade update email sent to {student.user.email} for course {course.name}.")
    
    except Grade.DoesNotExist:
        logger.error(f"Grade with ID {grade_id} does not exist.")
