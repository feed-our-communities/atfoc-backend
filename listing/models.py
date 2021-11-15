from django.db import models
from identity.models import Organization
from django.utils.translation import gettext_lazy as _

class TraitType(models.IntegerChoices):
    CANS = 0,_('is_cans')# one user should have only one pending application
    PERISHABLE = 1,_('is_perishable')

class Donation(models.Model):
    donation_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    description = models.TextField()
    picture = models.ImageField(upload_to='donations/', blank=False)
    expiration_date = models.DateField(blank=True, default=None)
    creation_time = models.DateTimeField(auto_now_add=True)
    deactivation_time = models.DateTimeField(null=True, blank=True, default=None)

class DonationTraits(models.Model):
    trait = models.IntegerField(
        choices=TraitType.choices,
        blank=False)
    donation_id = models.ForeignKey('Donation', on_delete=models.CASCADE)
