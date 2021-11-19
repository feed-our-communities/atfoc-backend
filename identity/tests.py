import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from identity import models
import json

EMAIL="email@example.com"
EMAIL_ADMIN="email-admin@example.com"
PASSWORD="password"

ORG_NAME="test_org"
ORG_ADDRESS="333 East Campus Mall Madison, WI"
ORG_EMAIL="test@test.com"
ORG_PHONE="+16081112222"
ORG_URL="test.com"
ORG_STATUS=models.OrgStatus.ACTIVE

MEMBERS_URL="/api/identity/org/members/"
"""
Fixtures
"""
@pytest.fixture
def organization(db) -> models.Organization:
    """
    Return an active organization
    """
    organization = models.Organization.objects.create(
        name = ORG_NAME,
        address = ORG_ADDRESS,
        email = ORG_EMAIL,
        phone = ORG_PHONE,
        url = ORG_URL,
        status = ORG_STATUS,
    )
    # create the two org role for the organization
    models.OrgRole.objects.create(organization=organization, is_admin=False)
    models.OrgRole.objects.create(organization=organization, is_admin=True)

    return organization

@pytest.fixture
def affiliated_non_admin_user(db, organization) -> User:
    """
    Return an non-admin User object(affiliated)
    """
    user = User.objects.create_user(EMAIL, EMAIL, PASSWORD)
    org_role = models.OrgRole.objects.get(organization=organization, is_admin=False)
    models.UserProfile.objects.create(user=user, org_role=org_role)
    return user

@pytest.fixture
def affiliated_admin_user(db, organization) -> User:
    """
    Return an admin User object(affiliated)
    """
    user = User.objects.create_user(EMAIL_ADMIN, EMAIL_ADMIN, PASSWORD)
    org_role = models.OrgRole.objects.get(organization=organization, is_admin=True)
    models.UserProfile.objects.create(user=user, org_role=org_role)
    return user

@pytest.fixture
def affiliated_non_admin_user_token(db, affiliated_non_admin_user) -> Token:
    """
    Return the token of the passed in User object
    """
    token = Token.objects.create(user=affiliated_non_admin_user)
    return token

@pytest.fixture
def affiliated_admin_user_token(db, affiliated_admin_user) -> Token:
    """
    Return the token of the passed in User object
    """
    token = Token.objects.create(user=affiliated_admin_user)
    return token

"""
Unit tests
"""
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
    organization = models.Organization.objects.create(
        name="name",
        address="address",
        email="email@example.com",
        phone="+16088675309",
        url="http://example.com",
        status=models.OrgStatus.ACTIVE
    )
    models.UserProfile.objects.create(
        user=user,
        org_role=models.OrgRole.objects.create(
            organization=organization,
            is_admin=False
        )
    )
    token = Token.objects.create(user=user)
    response = client.get("/api/identity/info/", HTTP_AUTHORIZATION='Token ' + token.key)
    expected = {
        "id": user.id,
        "email": "email@example.com",
        "first": "first",
        "last": "last",
        "organization": {
            "id": organization.id,
            "name": "name",
            "address": "address",
            "email": "email@example.com",
            "phone": "+16088675309",
            "url": "http://example.com",
            "status": 0
        },
        "is_org_admin": False
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

@pytest.mark.django_db()
def test_create_joinrequest(client):
    user = User.objects.create_user("email@example.com", "email@example.com", "password")
    user.first_name = "first"
    user.last_name = "last"
    user.save()
    organization = models.Organization.objects.create(
        name="name",
        address="address",
        email="email@example.com",
        phone="+16088675309",
        url="http://example.com",
        status=models.OrgStatus.ACTIVE
    )
    models.UserProfile.objects.create(
        user=user
    )
    token = Token.objects.create(user=user)
    data = {
        "note": "note",
        "status": models.ApplicationStatus.PENDING,
        "organization": organization.id
    }
    response = client.post("/api/identity/joinrequests/", data, HTTP_AUTHORIZATION='Token ' + token.key)
    join_request = models.JoinRequest.objects.get(id=response.data['id'])
    assert join_request.user.id == user.id
    assert join_request.organization.id == organization.id
    assert join_request.note == "note"
    assert join_request.status == models.ApplicationStatus.PENDING

@pytest.mark.django_db()
def test_list_joinrequest(client):
    user = User.objects.create_user("email@example.com", "email@example.com", "password")
    user.first_name = "first"
    user.last_name = "last"
    user.save()
    organization = models.Organization.objects.create(
        name="name",
        address="address",
        email="email@example.com",
        phone="+16088675309",
        url="http://example.com",
        status=models.OrgStatus.ACTIVE
    )
    models.UserProfile.objects.create(
        user=user
    )
    join_request = models.JoinRequest.objects.create(
        user=user,
        organization=organization,
        note="note",
        status=models.ApplicationStatus.PENDING
    )
    token = Token.objects.create(user=user)
    response = client.get("/api/identity/joinrequests/", HTTP_AUTHORIZATION='Token ' + token.key)
    expected_user = {
        "id": user.id,
        "email": "email@example.com",
        "first": "first",
        "last": "last"
    }
    expected_org = {
        "id": organization.id,
        "name": "name",
        "address": "address",
        "email": "email@example.com",
        "phone": "+16088675309",
        "url": "http://example.com",
        "status": 0
    }
    expected = {
        "id": join_request.id,
        "note": "note",
        "status": models.ApplicationStatus.PENDING,
        "user": expected_user,
        "organization": expected_org
    }
    assert json.loads(json.dumps(response.data[0])) == expected


"""
Tests for GET /api/identity/org/members/
"""
def test_get_members_success(client, db, affiliated_admin_user_token, organization,
        affiliated_non_admin_user, affiliated_admin_user):
    response = client.get(MEMBERS_URL + "?org_id=" + str(organization.id), 
        HTTP_AUTHORIZATION='Token ' + affiliated_admin_user_token.key)
    expected = {
       "members": [
           {
               "user_id": affiliated_non_admin_user.id,
                "first": affiliated_non_admin_user.first_name,
                "last": affiliated_non_admin_user.last_name
           }
        ],
       "admins" : [
           {
               "user_id": affiliated_admin_user.id,
                "first": affiliated_admin_user.first_name,
                "last": affiliated_admin_user.last_name
           }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected

def test_get_members_invalid_org(client, db, affiliated_admin_user_token):
    response = client.get(MEMBERS_URL + "?org_id=fake", 
        HTTP_AUTHORIZATION='Token ' + affiliated_admin_user_token.key)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_members_no_org(client, db, affiliated_admin_user_token):
    response = client.get(MEMBERS_URL, 
        HTTP_AUTHORIZATION='Token ' + affiliated_admin_user_token.key)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_members_no_access(client, db, affiliated_non_admin_user_token, organization):
    response = client.get(MEMBERS_URL + "?org_id=" + str(organization.id), 
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
