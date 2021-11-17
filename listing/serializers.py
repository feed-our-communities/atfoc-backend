from django.contrib.auth.models import User, Group
from rest_framework import serializers
from identity.models import Organization
from listing.models import TraitType, Donation, DonationTraits, Request, RequestTraits
from datetime import datetime
from django.utils import timezone

class DonationSerializer(serializers.Serializer):
    org_id = serializers.PrimaryKeyRelatedField(required=True, queryset=Organization.objects.all()) # required
    picture = serializers.ImageField(allow_empty_file=False, use_url=True) # required
    description = serializers.CharField()
    expiration_date = serializers.DateTimeField()
    deactivation_time = serializers.DateTimeField(required=False)
    traits = serializers.ListField(
        child=serializers.ChoiceField(choices=TraitType)
    )

    def soft_delete(self, instance):
        """
        Update operation right now only support soft delete
        """
        instance.deactivation_time = datetime.now(tz=timezone.utc) # TODO: Could expend to take incoming value later
        instance.save()

        return instance

    def create(self, validated_data):
        org = validated_data.get('org_id', None)
        picture = validated_data.get('picture', None)
        description = validated_data.get('description', "")
        expiration_date = validated_data.get('expiration_date', None)

        # create the donation listing
        donation = Donation.objects.create(
            organization = org,
            picture = picture,
            description = description,
            expiration_date = expiration_date,
            deactivation_time=None
        )

        # add the traits
        traits = validated_data.get('traits', [])
        for trait in traits:
            # do this so there are no repeat trait entries
            DonationTraits.objects.get_or_create(donation=donation, trait=trait)
        
        return donation

    def save(self):
        # modified from the django-rest source code. soft-delete when an instance is passed, otherwise create
        if self.instance is not None:
            self.instance = self.soft_delete(self.instance)
            assert self.instance is not None, (
                '`update()` did not return an object instance.'
            )
        else:
            self.instance = self.create(self.validated_data)
            assert self.instance is not None, (
                '`create()` did not return an object instance.')
        return self.instance

    def to_representation(self, instance):
        """
        Take in a donation instance
        """
        rep = dict()
        rep['donation_id'] = instance.donation_id
        rep['description'] = instance.description
        rep['expiration_date'] = instance.expiration_date
        rep['organization_id'] = instance.organization.id
        rep['picture'] = instance.picture.url
        trait_list = []
        traits = list(DonationTraits.objects.filter(donation=instance))
        for trait in traits:
            trait_list.append(trait.trait)
        rep['traits'] = trait_list
        return rep

class RequestSerializer(serializers.Serializer):
    org_id = serializers.PrimaryKeyRelatedField(required=True, queryset=Organization.objects.all()) # required
    description = serializers.CharField()
    deactivation_time = serializers.DateTimeField(required=False)
    traits = serializers.ListField(
        child=serializers.ChoiceField(choices=TraitType)
    )

    def soft_delete(self, instance):
        """
        Update operation right now only support soft delete
        """
        instance.deactivation_time = datetime.now(tz=timezone.utc) # TODO: Could expend to take incoming value later
        instance.save()

        return instance

    def create(self, validated_data):
        org = validated_data.get('org_id', None)
        description = validated_data.get('description', "")

        # create the request listing
        request = Request.objects.create(
            organization = org,
            description = description,
            deactivation_time=None
        )

        # add the traits
        traits = validated_data.get('traits', [])
        for trait in traits:
            # do this so there are no repeat trait entries
            RequestTraits.objects.get_or_create(request=request, trait=trait)
        
        return request

    def save(self):
        # modified from the django-rest source code. soft-delete when an instance is passed, otherwise create
        if self.instance is not None:
            self.instance = self.soft_delete(self.instance)
            assert self.instance is not None, (
                '`update()` did not return an object instance.'
            )
        else:
            self.instance = self.create(self.validated_data)
            assert self.instance is not None, (
                '`create()` did not return an object instance.')
        return self.instance

    def to_representation(self, instance):
        """
        Take in a request instance
        """
        rep = dict()
        rep['request_id'] = instance.request_id
        rep['description'] = instance.description
        rep['organization_id'] = instance.organization.id
        trait_list = []
        traits = list(RequestTraits.objects.filter(request=instance))
        for trait in traits:
            trait_list.append(trait.trait)
        rep['traits'] = trait_list
        return rep


