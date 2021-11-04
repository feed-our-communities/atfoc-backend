from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from identity import serializers
from identity import models
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import viewsets

# Create your views here.

class RegistrationView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = serializers.RegistrationSerializer

class UserInfoView(RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.RegistrationSerializer

    def get_object(self):
      queryset = self.get_queryset()
      obj = get_object_or_404(queryset, username=self.request.user.username)
      return obj

class CustomAuthToken(ObtainAuthToken):
    serializer_class = serializers.CustomAuthTokenSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class OrganizationViewSet(viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = models.Organization.objects.filter(status=models.OrgStatus.ACTIVE)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.OrganizationSerializer
