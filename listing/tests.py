import pytest
from datetime import datetime
import tempfile
from PIL import Image
from six import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework import status

from identity.models import Organization, OrgStatus, UserProfile, OrgRole
from listing.models import Donation, DonationTraits, Request, RequestTraits

EMAIL="email@example.com"
EMAIL_ADMIN="email-admin@example.com"
PASSWORD="password"
DONATION_URL="/api/listing/donations/"
REQUEST_URL="/api/listing/requests/"

ORG_NAME="test_org"
ORG_ADDRESS="333 East Campus Mall Madison, WI"
ORG_EMAIL="test@test.com"
ORG_PHONE="+16081112222"
ORG_URL="test.com"
ORG_STATUS=OrgStatus.ACTIVE

DONATION_DESCRIPTION="test description"
DONATION_PIC_NAME="image_test.jpg"
DONATION_EXPIREATION=datetime.now(tz=timezone.utc)

REQUEST_DESCRIPTION="test request description"

TEST_DIR = 'test_data'

"""
Fixtures
"""
@pytest.fixture
@override_settings(MEDIA_ROOT=(TEST_DIR))
def picture():
    tempfile.mkdtemp(TEST_DIR)
    image = BytesIO()
    Image.new('RGB', (100, 100)).save(image, 'JPEG')
    image.seek(0)

    return SimpleUploadedFile(
        DONATION_PIC_NAME,
        image.getvalue()
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
def affiliated_non_admin_user_token(db, affiliated_non_admin_user) -> Token:
    """
    Return the token of the passed in User object
    """
    token = Token.objects.create(user=affiliated_non_admin_user)
    return token

@pytest.fixture
@override_settings(MEDIA_ROOT=(TEST_DIR))
def init_donation_listing(db, organization, picture) -> Donation:
    """
    Create an initial donation listing for the organization
    """
    donation = Donation.objects.create(
        organization = organization,
        description = DONATION_DESCRIPTION,
        picture = picture,
        expiration_date = DONATION_EXPIREATION,
    )
    return donation

@pytest.fixture
@override_settings(MEDIA_ROOT=(TEST_DIR))
def init_donation_listing2(db, organization, picture) -> Donation:
    """
    Create an initial donation listing(with traits) for the organization
    """
    donation = Donation.objects.create(
        organization = organization,
        description = DONATION_DESCRIPTION,
        picture = picture,
        expiration_date = DONATION_EXPIREATION,
    )
    DonationTraits.objects.create(
        trait=0,
        donation=donation)
    return donation

@pytest.fixture
@override_settings(MEDIA_ROOT=(TEST_DIR))
def init_request_listing(db, organization) -> Request:
    """
    Create an initial request listing for the organization
    """
    request = Request.objects.create(
        organization = organization,
        description = REQUEST_DESCRIPTION,
    )
    return request

@pytest.fixture
@override_settings(MEDIA_ROOT=(TEST_DIR))
def init_request_listing2(db, organization, picture) -> Request:
    """
    Create an initial request listing(with traits) for the organization
    """
    request = Request.objects.create(
        organization = organization,
        description = REQUEST_DESCRIPTION,
    )
    RequestTraits.objects.create(
        trait=0,
        request=request)
    return request

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

def test_create_request_fixture(db, init_request_listing, organization):
    """
    Test to check if fixture is setup correctly
    """
    request_id=init_request_listing.request_id
    request_get = Request.objects.get(request_id=request_id)
    assert request_get.organization.id == organization.id
    assert request_get.description == REQUEST_DESCRIPTION

"""
Tests for GET /api/listing/donations/
"""
def test_get_donation_listing_all(client, db, 
    affiliated_non_admin_user_token, init_donation_listing, init_donation_listing2):
    response = client.get(DONATION_URL, HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    donation = init_donation_listing
    donation2 = init_donation_listing2
    expected = {
        "donations": [
            {
                "description": donation.description, 
                "donation_id": donation.donation_id,
                "expiration_date":donation.expiration_date,
                "organization_id": donation.organization.id,
                "picture":donation.picture.url,
                "traits": [] # no traits
            },
            {
                "description": donation2.description, 
                "donation_id": donation2.donation_id,
                "expiration_date":donation2.expiration_date,
                "organization_id": donation2.organization.id,
                "picture":donation2.picture.url,
                "traits": [0]
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
                "expiration_date":donation.expiration_date,
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
                "expiration_date":donation.expiration_date,
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

"""
Tests for POST /api/listing/donations/
"""
@override_settings(MEDIA_ROOT=(TEST_DIR))
def test_create_donation_listing_valid(client, db, affiliated_non_admin_user_token, organization, picture):
    org_id=organization.id
    description="test"
    expiration_date=datetime.now(tz=timezone.utc)
    trait1=0
    trait2=1
    post_data = {
        "org_id": org_id, 
        "description": description,
        "picture": picture,
        "expiration_date": expiration_date,
        "traits": [trait1, trait2]
    }

    response = client.post(DONATION_URL,
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key,
        data=post_data,)

    created_donation = Donation.objects.get(donation_id=response.data["donation_id"])
    traits = list(DonationTraits.objects.filter(donation=created_donation).values('trait'))

    assert response.status_code == status.HTTP_201_CREATED
    assert created_donation.organization.id == org_id
    assert created_donation.description == description
    assert created_donation.expiration_date == expiration_date
    assert [traits[0]["trait"],traits[1]["trait"]] == [trait1, trait2]
    assert created_donation.deactivation_time == None

def test_create_donation_listing_org_invalid(client, db, affiliated_non_admin_user_token, picture):
    org_id="fake"
    description="test"
    expiration_date=datetime.now(tz=timezone.utc)
    trait1=0
    trait2=1
    post_data = {
        "org_id": org_id, 
        "description": description,
        "picture": picture,
        "expiration_date": expiration_date,
        "traits": [trait1, trait2]
    }

    response = client.post(DONATION_URL,
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key,
        data=post_data,)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

"""
Tests for DELETE /api/listing/donations/
"""
def test_delete_donation_listing(client, db, affiliated_non_admin_user_token, init_donation_listing):
    post_data = {
        "donation_id": init_donation_listing.donation_id, 
    }

    response = client.delete(DONATION_URL,
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key,
        data=post_data,
        content_type='application/json')
    
    donation = Donation.objects.get(donation_id=init_donation_listing.donation_id)

    assert response.status_code == status.HTTP_200_OK
    assert donation.deactivation_time != None

def test_delete_donation_listing_invalid_donation(client, db, affiliated_non_admin_user_token):
    post_data = {
        "donation_id": "fake", 
    }

    response = client.delete(DONATION_URL,
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key,
        data=post_data,
        content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_delete_donation_listing_missing_param(client, db, affiliated_non_admin_user_token):
    post_data = {
        "donation_id2": "fake", 
    }

    response = client.delete(DONATION_URL,
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key,
        data=post_data,
        content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

"""
Tests for GET /api/listing/requests/
"""
def test_get_request_listing_all(client, db, 
    affiliated_non_admin_user_token, init_request_listing, init_request_listing2):
    response = client.get(REQUEST_URL, HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    request = init_request_listing
    request2 = init_request_listing2
    expected = {
        "requests": [
            {
                "description": request.description, 
                "request_id": request.request_id,
                "organization_id": request.organization.id,
                "traits": [] # no traits
            },
            {
                "description": request2.description, 
                "request_id": request2.request_id,
                "organization_id": request2.organization.id,
                "traits": [0]
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected

def test_get_request_listing_filter_by_org(client, db, affiliated_non_admin_user_token, init_request_listing):
    request = init_request_listing
    response = client.get(REQUEST_URL + "?org_id=" + str(request.organization.id), 
                            HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    expected = {
        "requests": [
            {
                "request_id": request.request_id,
                "description": request.description, 
                "organization_id": request.organization.id,
                "traits": [] # no traits
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected

def test_get_request_listing_filter_by_status(client, db, affiliated_non_admin_user_token, init_request_listing):
    request = init_request_listing
    response = client.get(REQUEST_URL + "?status=active", HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    expected = {
        "requests": [
            {
                "request_id": request.request_id,
                "description": request.description, 
                "organization_id": request.organization.id,
                "traits": [] # no traits
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected

def test_get_request_listing_filter_by_org_invalid(client, db, affiliated_non_admin_user_token):
    response = client.get(REQUEST_URL + "?org_id=fake", HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_request_listing_filter_by_status_invalid(client, db, affiliated_non_admin_user_token):
    response = client.get(REQUEST_URL + "?status=invalid", HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_request_listing_empty(client, db, affiliated_non_admin_user_token):
    response = client.get(REQUEST_URL + "?status=inactive", HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key)
    assert response.status_code == status.HTTP_204_NO_CONTENT

"""
Tests for POST /api/listing/requests/
"""
@override_settings(MEDIA_ROOT=(TEST_DIR))
def test_create_request_listing_valid(client, db, affiliated_non_admin_user_token, organization):
    org_id=organization.id
    description="test"
    trait1=0
    trait2=1
    post_data = {
        "org_id": org_id, 
        "description": description,
        "traits": [trait1, trait2]
    }

    response = client.post(REQUEST_URL,
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key,
        data=post_data,)

    created_request = Request.objects.get(request_id=response.data["request_id"])
    traits = list(RequestTraits.objects.filter(request=created_request).values('trait'))

    assert response.status_code == status.HTTP_201_CREATED
    assert created_request.organization.id == org_id
    assert created_request.description == description
    assert [traits[0]["trait"],traits[1]["trait"]] == [trait1, trait2]
    assert created_request.deactivation_time == None

def test_create_request_listing_org_invalid(client, db, affiliated_non_admin_user_token):
    org_id="fake"
    description="test"
    trait1=0
    trait2=1
    post_data = {
        "org_id": org_id, 
        "description": description,
        "traits": [trait1, trait2]
    }

    response = client.post(REQUEST_URL,
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key,
        data=post_data,)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

"""
Tests for DELETE /api/listing/requests/
"""
def test_delete_request_listing(client, db, affiliated_non_admin_user_token, init_request_listing):
    post_data = {
        "request_id": init_request_listing.request_id, 
    }

    response = client.delete(REQUEST_URL,
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key,
        data=post_data,
        content_type='application/json')
    
    request = Request.objects.get(request_id=init_request_listing.request_id)

    assert response.status_code == status.HTTP_200_OK
    assert request.deactivation_time != None

def test_delete_request_listing_invalid_request(client, db, affiliated_non_admin_user_token):
    post_data = {
        "request_id": "fake", 
    }

    response = client.delete(REQUEST_URL,
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key,
        data=post_data,
        content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_delete_request_listing_missing_param(client, db, affiliated_non_admin_user_token):
    post_data = {
        "request_id1": "fake", 
    }

    response = client.delete(REQUEST_URL,
        HTTP_AUTHORIZATION='Token ' + affiliated_non_admin_user_token.key,
        data=post_data,
        content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST