from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

from identity import models


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        fields = ['id', 'name','address', 'email', 'phone', 'url', 'status']

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True, required=True)
    email = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())], required=True)
    first = serializers.CharField(source="first_name", max_length=128, min_length=1, required=False)
    last = serializers.CharField(source="last_name", max_length=128, min_length=1, required=False)
    organization = OrganizationSerializer(source='userprofile.org_role.organization', read_only=True)
    is_org_admin = serializers.BooleanField(source='userprofile.org_role.is_admin', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'password', 'email', 'first', 'last', 'organization', 'is_org_admin']

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        first = validated_data['first_name']
        last = validated_data['last_name']
        user = User.objects.create_user(email, email, password)
        user.first_name = first
        user.last_name = last
        user.save()
        profile = models.UserProfile.objects.create(user=user)
        profile.save()
        return user
class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        username = attrs.get('email')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class OrgApplicationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    status = serializers.HiddenField(
        default=models.ApplicationStatus.PENDING
    )
    class Meta:
        model = models.OrgApplication
        fields = ["id", "user", "name", "address", "phone", "email", "url", "status"]

class JoinRequestSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = models.JoinRequest
        fields = ['id', 'user', 'organization', 'note', 'status']


class OrgMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ['user', 'org_role']
    
    def to_representation(self, instance):
        rep = dict()
        rep['user_id'] = instance.user.id
        rep['first'] = instance.user.first_name
        rep['last'] = instance.user.last_name
        return rep
