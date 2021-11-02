import pytest
from django.contrib.auth.models import User

# Create your tests here.

@pytest.mark.django_db()
def test_login(client):
    User.objects.create_user("username", "email@example.com", "password")
    response = client.post("/api/identity/login/", {
        "username": "username",
        "password": "password"
    })
    assert len(response.data["token"]) > 1

@pytest.mark.django_db()
def test_register(client):
    client.post("/api/identity/register/", {
        "username": "username",
        "password": "password",
        "email": "email@example.com"
    })
    user = User.objects.get(username="username", email="email@example.com")
    assert user.check_password("password")
