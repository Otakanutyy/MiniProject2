from celery import shared_task
from django.utils.timezone import now
from .models import AttendanceWindow

@shared_task
def close_window_task(window_id):
    try:
        window = AttendanceWindow.objects.get(id=window_id)
        window.close_window()
    except AttendanceWindow.DoesNotExist:
        pass
