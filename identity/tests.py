import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from identity import models

# Create your tests here.

@pytest.mark.django_db()
def test_login(client):
    User.objects.create_user("email@example.com", "email@example.com", "password")
    response = client.post("/api/identity/login/", {
        "email": "email@example.com",
        "password": "password"
    })
    assert len(response.data["token"]) > 1

@pytest.mark.django_db()
def test_register(client):
    client.post("/api/identity/register/", {
        "email": "email@example.com",
        "password": "password"
    })
    user = User.objects.get(username="email@example.com", email="email@example.com")
    assert user.check_password("password")

@pytest.mark.django_db()
def test_organization(client):
    models.Organization.objects.create(
        name="name",
        address="address",
        email="email@example.com",
        phone="608-867-5309",
        url="example.com",
        status=models.OrgStatus.ACTIVE
    )
    user = User.objects.create_user("email@example.com", "email@example.com", "password")
    token = Token.objects.create(user=user)
    response = client.get("/api/identity/organization/", HTTP_AUTHORIZATION='Token ' + token.key)
    expected = {
        "id": 1,
        "name": "name",
        "address": "address",
        "email": "email@example.com",
        "phone": "608-867-5309",
        "url": "example.com",
        "status": 0
    }
    assert dict(response.data[0]) == expected
