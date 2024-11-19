from notifications.tasks import send_daily_report, send_weekly_performance_report
from users.models import User
import pytest


@pytest.mark.django_db
def test_send_daily_report_task(mailoutbox):
    admin_user = User.objects.create(
        username="admin", email="admin@example.com", role="admin"
    )
    result = send_daily_report()
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "Daily Attendance and Grade Report"
    assert "Daily Attendance and Grade Summary" in mailoutbox[0].body
    assert result == f"Sent daily report to 1 admins."


@pytest.mark.django_db
def test_send_weekly_performance_report_task(mailoutbox):
    student_user = User.objects.create(
        username="student1", email="student1@example.com", role="student"
    )
    result = send_weekly_performance_report()
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "Weekly Performance Report"
    assert "Your performance for this week" in mailoutbox[0].body
    assert result == f"Sent weekly reports to 1 students."