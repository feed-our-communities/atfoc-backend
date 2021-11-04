from rest_framework import serializers
from django.contrib.auth.models import User
from identity import models
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True, required=True)
    email = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())], required=True)
    first = serializers.CharField(max_length=128, min_length=1, required=False)
    last = serializers.CharField(max_length=128, min_length=1, required=False)

    class Meta:
        model = User
        fields = ['id', 'password', 'email', 'first', 'last']

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        first = validated_data.get('first', "")
        last = validated_data.get('last', "")
        user = User.objects.create_user(email, email, password)
        user.first_name = first
        user.last_name = last
        user.save()
        profile = models.UserProfile.objects.create(user=user)
        profile.save()
        return user

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'email': instance.email,
            'first': instance.first_name,
            'last': instance.last_name
        }

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

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        fields = ['id', 'name','address', 'email', 'phone', 'url', 'status']

class OrgApplicationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = models.OrgApplication
        fields = ["id", "user", "name", "address", "phone", "email", "url"]
