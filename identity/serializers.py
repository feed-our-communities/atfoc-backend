from rest_framework import serializers
from django.contrib.auth.models import User
from identity.models import UserProfile
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True, required=True)
    email = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())], required=True)
 
    class Meta:
        model = User
        fields = ['id', 'password', 'email']

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(email, email, password)
        
        profile = UserProfile.objects.create(user=user)
        profile.save()
        return user

    def to_representation(self, instance):
        return_rep = dict()
        return_rep['id'] = instance.id
        return_rep['email'] = instance.email
        return return_rep

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
