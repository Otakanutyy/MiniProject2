import datetime
import pytest
from students.models import Student
from users.models import User


@pytest.mark.django_db
def test_student_creation():
    user = User.objects.create(username="student1", role="student")
  
    Student.objects.filter(user=user).delete()

    student = Student.objects.create(
        user=user,
        name="Student One",
        email="student1@example.com",
        dob=datetime.date(2000, 1, 1)
    )

    assert student.user.username == "student1"
    assert student.dob == datetime.date(2000, 1, 1)
    assert student.registration_date is not None