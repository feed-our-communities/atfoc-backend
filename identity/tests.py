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

MEMBERS_URL="/api/identity/org/{org_id}/members/"
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
def test_login_missing_param(client):
    response = client.post("/api/identity/register/", {
        "email2": "email@example.com",
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db()
def test_login_wrong_password(client):
    User.objects.create_user("email@example.com", "email@example.com", "password")
    response = client.post("/api/identity/register/", {
         "email": "email@example.com",
        "password": "password2",
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST

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
        "is_org_admin": False,
        "is_site_admin": False,
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
def test_create_organization(client):
    user = User.objects.create_user("email@example.com", "email@example.com", "password")
    token = Token.objects.create(user=user)
    ORG_NAME = "name2"
    ORG_ADDRESS = "address2"
    ORG_EMAIL = "email@example.com"
    ORG_PHONE = "+16088675309"
    ORG_URL_2 = "http://example.com"
    ORG_STATUS = 0
    data = {
        "name": ORG_NAME,
        "address": ORG_ADDRESS,
        "email": ORG_EMAIL,
        "phone": ORG_PHONE,
        "url": ORG_URL_2,
        "status": ORG_STATUS
    }
    response = client.post("/api/identity/organization/", data, HTTP_AUTHORIZATION='Token ' + token.key)
    assert response.status_code == status.HTTP_201_CREATED
    organization = models.Organization.objects.get(id=response.data["id"])

    assert organization.name == ORG_NAME
    assert organization.address == ORG_ADDRESS
    assert organization.email == ORG_EMAIL
    assert str(organization.phone.national_number) == "6088675309"
    assert organization.url == ORG_URL_2
    assert organization.status == ORG_STATUS

@pytest.mark.django_db()
def test_get_organization(client):
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
    response = client.get("/api/identity/organization/"+str(organization.id)+"/", HTTP_AUTHORIZATION='Token ' + token.key)
    expected = {
        "id": organization.id,
        "name": "name",
        "address": "address",
        "email": "email@example.com",
        "phone": "+16088675309",
        "url": "http://example.com",
        "status": 0
    }
    assert response.data == expected

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
        "url": "http://example.com",
        "status": models.ApplicationStatus.PENDING
    }
    assert dict(response.data[0]) == expected

@pytest.mark.django_db()
def test_withdraw_application(client):
    user = User.objects.create_user("email@example.com", "email@example.com", "password")
    org_application = models.OrgApplication.objects.create(
        name="name",
        user=user,
        address="address",
        email="email@example.com",
        phone="+16088675309",
        url="http://example.com"
    )
    token = Token.objects.create(user=user)
    client.patch(
        "/api/identity/application/"+str(org_application.id)+"/",
        {"status": models.ApplicationStatus.WITHDRAWN},
        HTTP_AUTHORIZATION='Token ' + token.key,
        content_type='application/json'
    )
    org_application.refresh_from_db()
    assert org_application.status == models.ApplicationStatus.WITHDRAWN

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
        'is_site_admin': False,
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

@pytest.mark.django_db()
def test_withdraw_joinrequest(client):
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
    client.patch("/api/identity/joinrequests/" + str(join_request.id) + "/", {
        "status": models.ApplicationStatus.WITHDRAWN,
    }, HTTP_AUTHORIZATION='Token ' + token.key, content_type='application/json')
    join_request.refresh_from_db()
    assert join_request.status == models.ApplicationStatus.WITHDRAWN

"""
Tests for GET /api/identity/org/{org_id}/members/
"""
def test_get_members_success(client, db, affiliated_admin_user_token, organization,
        affiliated_non_admin_user, affiliated_admin_user):
    response = client.get(MEMBERS_URL.format(org_id=str(organization.id)), 
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
    response = client.get(MEMBERS_URL.format(org_id="fake"), 
        HTTP_AUTHORIZATION='Token ' + affiliated_admin_user_token.key)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_members_no_access(client, db, affiliated_non_admin_user_token, organization):
    response = client.get(MEMBERS_URL.format(org_id=str(organization.id)), 
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

"""
Tests for PUT /api/identity/org/members/
Make an user a member of an organization
Or update user's admin status
"""
def test_add_non_admin_member_success(client, db, affiliated_admin_user_token, organization):
    # created an unaffilicated user
    EMAIL = "email@example.com"
    user = User.objects.create_user(EMAIL, "email@example.com", "password")
    models.UserProfile.objects.create(user=user, org_role=None)

    is_admin = False
    post_data = {
        "user_id": str(user.id), 
        "is_admin": is_admin
    }
    response = client.put(MEMBERS_URL.format(org_id=str(organization.id)), 
        HTTP_AUTHORIZATION='Token ' + affiliated_admin_user_token.key,
        content_type='application/json',
        data=post_data)

    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.get(username=EMAIL)
    assert models.OrgRole.objects.get(organization=organization, userprofile=user.userprofile).is_admin == is_admin

def test_add_admin_member_success(client, db, affiliated_admin_user_token, organization):
    # created an unaffilicated user
    EMAIL = "email@example.com"
    user = User.objects.create_user(EMAIL, "email@example.com", "password")
    models.UserProfile.objects.create(user=user, org_role=None)

    is_admin = True
    post_data = {
        "user_id": str(user.id), 
        "is_admin": is_admin
    }
    response = client.put(MEMBERS_URL.format(org_id=str(organization.id)), 
        HTTP_AUTHORIZATION='Token ' + affiliated_admin_user_token.key,
        content_type='application/json',
        data=post_data)

    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.get(username=EMAIL)
    assert models.OrgRole.objects.get(organization=organization, userprofile=user.userprofile).is_admin == is_admin

def test_add_members_no_access(client, db, affiliated_non_admin_user_token, organization,
        affiliated_non_admin_user):
    post_data = {
        "user_id": str(affiliated_non_admin_user.id), 
        "is_admin": "False"
    }
    response = client.put(MEMBERS_URL.format(org_id=str(organization.id)), 
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key,
        content_type='application/json',
        data=post_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_change_admin_member_success(client, db, affiliated_admin_user_token, affiliated_non_admin_user, organization):
    is_admin = "True"
    post_data = {
        "user_id": str(affiliated_non_admin_user.id), 
        "is_admin": is_admin
    }
    response = client.put(MEMBERS_URL.format(org_id=str(organization.id)), 
        HTTP_AUTHORIZATION='Token ' + affiliated_admin_user_token.key,
        content_type='application/json',
        data=post_data)

    assert response.status_code == status.HTTP_201_CREATED
    affiliated_non_admin_user.refresh_from_db()
    assert affiliated_non_admin_user.userprofile.org_role.is_admin == True

"""
Tests for DELETE /api/identity/org/members/
Remove an user from the organization
"""

def test_remove_member_success(client, db, affiliated_admin_user_token, organization,
        affiliated_non_admin_user):
    user = affiliated_non_admin_user

    post_data = {
        "user_id": str(user.id), 
    }
    response = client.delete(MEMBERS_URL.format(org_id=str(organization.id)), 
        HTTP_AUTHORIZATION='Token ' + affiliated_admin_user_token.key,
        content_type='application/json',
        data=post_data)

    assert response.status_code == status.HTTP_200_OK
    user = User.objects.get(username=affiliated_non_admin_user.username)
    assert user.userprofile.org_role == None

    affiliated_non_admin_user.save()

def test_remove_member_self_success(client, db, organization, affiliated_non_admin_user, affiliated_non_admin_user_token):
    user = affiliated_non_admin_user
    post_data = {
        "user_id": str(user.id), 
    }
    response = client.delete(MEMBERS_URL.format(org_id=str(organization.id)), 
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key,
        content_type='application/json',
        data=post_data)

    assert response.status_code == status.HTTP_200_OK
    user = User.objects.get(username=affiliated_non_admin_user.username)
    assert user.userprofile.org_role == None

    affiliated_non_admin_user.save()
