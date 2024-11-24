from celery import shared_task
from analytics.models import APIRequestLog, ActiveUser
from courses.models import Enrollment
from analytics.models import PopularCourse
from django.db import models
from django.db.models import Count
import logging
logger = logging.getLogger(__name__)


@shared_task
def update_active_users():
    logs = APIRequestLog.objects.values('user').annotate(api_calls=Count('id'))

    for log in logs:
        ActiveUser.objects.update_or_create(
            user_id=log['user'],
            defaults={'api_calls': log['api_calls']}
        )


@shared_task
def update_popular_courses():
    courses = Enrollment.objects.values('course').annotate(views=models.Count('id'))
    for course in courses:
        PopularCourse.objects.update_or_create(
            course_id=course['course'],
            defaults={'views': course['views']}
        )
