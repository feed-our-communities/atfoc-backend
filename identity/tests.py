import pytest
from django.contrib.auth.models import User
from rest_framework.test import force_authenticate

# Create your tests here.

@pytest.mark.django_db()
def test_login(client):
    User.objects.create_user("email@example.com", "email@example.com", "password")
    response = client.post("/api/identity/login/", {
        "email": "email@example.com",
        "password": "password"
    })
    print(response)
    assert len(response.data["token"]) > 1

@pytest.mark.django_db()
def test_register(client):
    client.post("/api/identity/register/", {
        "email": "email@example.com",
        "password": "password"
    })
    user = User.objects.get(username="email@example.com", email="email@example.com")
    assert user.check_password("password")
