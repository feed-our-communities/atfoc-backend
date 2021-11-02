from rest_framework import serializers
from django.contrib.auth.models import User
from identity.models import UserProfile
from rest_framework.validators import UniqueValidator

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True, required=True)
    username = serializers.CharField( validators=[UniqueValidator(queryset=User.objects.all())], required=True)
 
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(username, email, password)
        
        profile = UserProfile.objects.create(user=user)
        profile.save()
        return user

    def to_representation(self, instance):
        return_rep = dict()
        return_rep['id'] = instance.id
        return_rep['username'] = instance.username
        return_rep['email'] = instance.email
        return return_rep
