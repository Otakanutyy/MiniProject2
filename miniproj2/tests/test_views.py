from rest_framework.test import APIClient
import pytest
from students.models import Student
from users.models import User
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_student_list_as_admin():
    """
    Test that an admin can view the list of students.
    """
    admin_user = User.objects.create(username="admin", role="admin")
    client = APIClient()
    client.force_authenticate(user=admin_user)
    response = client.get("/api/students/all_profiles/")
    assert response.status_code == HTTP_200_OK

