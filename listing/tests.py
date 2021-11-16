from collections import namedtuple
import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from identity.models import Organization, OrgStatus, UserProfile, OrgRole
from listing.models import Donation
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
from django.test import override_settings
import tempfile
from django.utils import timezone
import json

EMAIL="email@example.com"
EMAIL_ADMIN="email-admin@example.com"
PASSWORD="password"
DONATION_URL="/api/listing/donations/"

ORG_NAME="test_org"
ORG_ADDRESS="333 East Campus Mall Madison, WI"
ORG_EMAIL="test@test.com"
ORG_PHONE="+16081112222"
ORG_URL="test.com"
ORG_STATUS=OrgStatus.ACTIVE

DONATION_DESCRIPTION="test description"
DONATION_PIC_NAME="image_test.jpg"
DONATION_EXPIREATION=datetime.now(tz=timezone.utc)

TEST_DIR = 'test_data'

@pytest.fixture
@override_settings(MEDIA_ROOT=(TEST_DIR))
def picture():
    tempfile.mkdtemp(TEST_DIR)
    return SimpleUploadedFile(
            DONATION_PIC_NAME,
            b"bytes for an image..."
    )

@pytest.fixture
def organization(db) -> Organization:
    """
    Return an active organization
    """
    organization = Organization.objects.create(
        name = ORG_NAME,
        address = ORG_ADDRESS,
        email = ORG_EMAIL,
        phone = ORG_PHONE,
        url = ORG_URL,
        status = ORG_STATUS,
    )
    # create the two org role for the organization
    OrgRole.objects.create(organization=organization, is_admin=False)
    OrgRole.objects.create(organization=organization, is_admin=True)

    return organization

@pytest.fixture
def affiliated_non_admin_user(db, organization) -> User:
    """
    Return an non-admin User object(affiliated)
    """
    user = User.objects.create_user(EMAIL, EMAIL, PASSWORD)
    org_role = OrgRole.objects.get(organization=organization, is_admin=False)
    UserProfile.objects.create(user=user, org_role=org_role)
    return user

@pytest.fixture
def affiliated_admin_user(db, organization) -> User:
    """
    Return an admin User object(affiliated)
    """
    user = User.objects.create_user(EMAIL_ADMIN, EMAIL_ADMIN, PASSWORD)
    org_role = OrgRole.objects.get(organization=organization, is_admin=True)
    UserProfile.objects.create(user=user, org_role=org_role)
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

@pytest.fixture
@override_settings(MEDIA_ROOT=(TEST_DIR))
def init_donation_listing(db, organization, picture) -> Donation:
    """
    Create an initial listing for the organization
    """
    donation = Donation.objects.create(
        organization = organization,
        description = DONATION_DESCRIPTION,
        picture = picture,
        expiration_date = DONATION_EXPIREATION,
    )
    return donation


def test_create_org_fixture(db, organization):
    """
    Test to check if fixture is setup correctly
    """
    org_id=organization.id
    organization_get = Organization.objects.get(id=org_id)
    assert organization_get.name == ORG_NAME
    assert organization_get.address == ORG_ADDRESS
    assert organization_get.email == ORG_EMAIL
    assert organization_get.phone == ORG_PHONE
    assert organization_get.url == ORG_URL
    assert organization_get.status == ORG_STATUS

def test_create_donation_fixture(db, init_donation_listing, organization):
    """
    Test to check if fixture is setup correctly
    """
    donation_id=init_donation_listing.donation_id
    donation_get = Donation.objects.get(donation_id=donation_id)
    assert donation_get.organization.id == organization.id
    assert donation_get.description == DONATION_DESCRIPTION
    assert donation_get.expiration_date == DONATION_EXPIREATION

def test_get_donation_listing_all(client, db, affiliated_non_admin_user_token, init_donation_listing):
    response = client.get(DONATION_URL, HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    donation = init_donation_listing
    expected = {
        "donations": [
            {
                "description": donation.description, 
                "donation_id": donation.donation_id,
                "expiration date":donation.expiration_date,
                "organization_id": donation.organization.id,
                "picture":donation.picture.url,
                "traits": [] # no traits
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected

def test_get_donation_listing_filter_by_org(client, db, affiliated_non_admin_user_token, init_donation_listing):
    donation = init_donation_listing
    response = client.get(DONATION_URL + "?org_id=" + str(donation.organization.id), HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    expected = {
        "donations": [
            {
                "description": donation.description, 
                "donation_id": donation.donation_id,
                "expiration date":donation.expiration_date,
                "organization_id": donation.organization.id,
                "picture":donation.picture.url,
                "traits": [] # no traits
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected

def test_get_donation_listing_filter_by_status(client, db, affiliated_non_admin_user_token, init_donation_listing):
    donation = init_donation_listing
    response = client.get(DONATION_URL + "?status=active", HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    expected = {
        "donations": [
            {
                "description": donation.description, 
                "donation_id": donation.donation_id,
                "expiration date":donation.expiration_date,
                "organization_id": donation.organization.id,
                "picture":donation.picture.url,
                "traits": [] # no traits
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected

def test_get_donation_listing_filter_by_org_invalid(client, db, affiliated_non_admin_user_token):
    response = client.get(DONATION_URL + "?org_id=fake", HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_donation_listing_filter_by_status_invalid(client, db, affiliated_non_admin_user_token):
    response = client.get(DONATION_URL + "?status=invalid", HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_donation_listing_empty(client, db, affiliated_non_admin_user_token):
    response = client.get(DONATION_URL + "?status=inactive", HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    assert response.status_code == status.HTTP_204_NO_CONTENT