from celery import shared_task
from django.utils.timezone import now

'''@shared_task
def close_expired_windows():
    current_time = now()
    expired_windows = AttendanceWindow.objects.filter(end_time__lte=current_time, is_open=True)

    for window in expired_windows:
        window.close_window()'''