from collections import namedtuple
import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from identity.models import Organization, OrgStatus, UserProfile, OrgRole
from listing.models import Donation
import tempfile
import datetime
import json

# Create your tests here.

EMAIL="email@example.com"
EMAIL_ADMIN="email-admin@example.com"
PASSWORD="password"
URL="/api/listing/donations/"

ORG_NAME="test_org"
ORG_ADDRESS="333 East Campus Mall Madison, WI"
ORG_EMAIL="test@test.com"
ORG_PHONE="+16081112222"
ORG_URL="test.com"
ORG_STATUS=OrgStatus.ACTIVE

DONATION_DESCRIPTION="test description"
DONATION_PIC=tempfile.NamedTemporaryFile(suffix=".jpg")
DONATION_EXPIREATION=datetime.date.today()



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
def affiliated_non_admin_user(db) -> User:
    """
    Return an non-admin User object(affiliated)
    """
    user = User.objects.create_user(EMAIL, EMAIL, PASSWORD)
    org_role = OrgRole.objects.all().filter(is_admin=False)
    UserProfile.objects.create(user=user, org_role=org_role)
    return user

@pytest.fixture
def affiliated_admin_user(db) -> User:
    """
    Return an admin User object(affiliated)
    """
    user = User.objects.create_user(EMAIL_ADMIN, EMAIL_ADMIN, PASSWORD)
    org_role = OrgRole.objects.all().filter(is_admin=True)
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
def init_donation_listing(db, organization) -> Donation:
    """
    Create an initial listing for the organization
    """
    donation = Donation.objects.create(
        organization = organization,
        description = DONATION_DESCRIPTION,
        picture = DONATION_PIC,
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

def test_create_donation_fixture(db, donation, organization):
    """
    Test to check if fixture is setup correctly
    """
    donation_id=donation.donation_id
    donation_get = Donation.objects.get(donation_id=donation_id)
    assert donation_get.organization.id == organization.id
    assert donation_get.description == DONATION_DESCRIPTION
    assert donation_get.picture == DONATION_PIC.name
    assert donation_get.expiration_date == DONATION_EXPIREATION

