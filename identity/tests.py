from collections import namedtuple
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
        "password": "password",
        "first": "first",
        "last": "last"
    })
    user = User.objects.get(username="email@example.com")
    assert user.email == "email@example.com"
    assert user.first_name == "first"
    assert user.last_name == "last"
    assert user.check_password("password")

@pytest.mark.django_db()
def test_info(client):
    user = User.objects.create_user("email@example.com", "email@example.com", "password")
    user.first_name = "first"
    user.last_name = "last"
    user.save()
    token = Token.objects.create(user=user)
    response = client.get("/api/identity/info/", HTTP_AUTHORIZATION='Token ' + token.key)
    expected = {
        "id": user.id,
        "email": "email@example.com",
        "first": "first",
        "last": "last"
    }
    assert response.data == expected

@pytest.mark.django_db()
def test_list_organization(client):
    organization = models.Organization.objects.create(
        name="name",
        address="address",
        email="email@example.com",
        phone="+16088675309",
        url="http://example.com",
        status=models.OrgStatus.ACTIVE
    )
    user = User.objects.create_user("email@example.com", "email@example.com", "password")
    token = Token.objects.create(user=user)
    response = client.get("/api/identity/organization/", HTTP_AUTHORIZATION='Token ' + token.key)
    expected = {
        "id": organization.id,
        "name": "name",
        "address": "address",
        "email": "email@example.com",
        "phone": "+16088675309",
        "url": "http://example.com",
        "status": 0
    }
    assert dict(response.data[0]) == expected

@pytest.mark.django_db()
def test_create_application(client):
    user = User.objects.create_user("email@example.com", "email@example.com", "password")
    token = Token.objects.create(user=user)
    data = {
        "name": "name",
        "address": "address",
        "phone": "+16088675309",
        "email": "email@example.com",
        "url": "http://example.com"
    }
    response = client.post("/api/identity/application/", data, HTTP_AUTHORIZATION='Token ' + token.key)
    print(response.data)
    application = models.OrgApplication.objects.get(id=response.data["id"])
    assert application.user == user
    assert application.name == "name"
    assert application.address == "address"
    assert application.phone == "+16088675309"
    assert application.email == "email@example.com"
    assert application.url == "http://example.com"

@pytest.mark.django_db()
def test_list_application(client):
    user = User.objects.create_user("email@example.com", "email@example.com", "password")
    organization = models.OrgApplication.objects.create(
        name="name",
        user=user,
        address="address",
        email="email@example.com",
        phone="+16088675309",
        url="http://example.com"
    )
    token = Token.objects.create(user=user)
    response = client.get("/api/identity/application/", HTTP_AUTHORIZATION='Token ' + token.key)
    expected = {
        "id": organization.id,
        "name": "name",
        "address": "address",
        "email": "email@example.com",
        "phone": "+16088675309",
        "url": "http://example.com"
    }
    assert dict(response.data[0]) == expected
