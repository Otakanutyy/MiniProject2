import pytest
from rest_framework.test import APIClient
from users.models import User
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_course_create_permission_as_teacher():
    teacher_user = User.objects.create(username="teacher1", role="teacher")
    client = APIClient()
    client.force_authenticate(user=teacher_user)
    payload = {
        "name": "Math 101",
        "description": "Basic Math Course",
    }
    response = client.post("/api/courses/", payload)
    assert response.status_code == 201
    assert response.data["instructor"] == teacher_user.id


@pytest.mark.django_db
def test_course_create_permission_as_student():
    student_user = User.objects.create(username="student1", role="student")
    client = APIClient()
    client.force_authenticate(user=student_user)
    payload = {"name": "Math 101", "description": "Basic Math Course"}
    response = client.post("/api/courses/", payload)
    assert response.status_code == HTTP_403_FORBIDDEN