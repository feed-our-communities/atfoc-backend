from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

# Create your models here.

class UserProfile(models.Model):
    """
    Profile describes an user
    """
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey('Organization', on_delete=models.SET_DEFAULT, default=None, null=True)
    is_admin=models.BooleanField(default=False)
    
class Organization(models.Model):
    name=models.CharField(max_length=20, blank=False)
    address=models.CharField(max_length=50, blank=False)
    email=models.EmailField(blank=False)
    phone=PhoneNumberField(null=False, unique=False, blank=False) 
    url=models.URLField(default=None)

class ApplicationStatus(models.IntegerChoices):
    PENDING = 0,_('Pending')
    APRROVED = 1,_('Approved')
    DENIED = 2,_('Denied')

class JoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, blank=False) 
    note = models.TextField(default=None, blank=True)
    status = models.IntegerField(
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
class OrgApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    status = models.IntegerField(
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
    )
    name=models.CharField(max_length=20, blank=False)
    address=models.CharField(max_length=50, blank=False)
    phone=PhoneNumberField(blank=False) 
    email=models.EmailField(default=None, blank=True)
    url=models.URLField(default=None, blank=True) 
