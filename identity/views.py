from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from identity import serializers
from identity import models

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

class OrgApplicationViewSet(viewsets.mixins.UpdateModelMixin, viewsets.mixins.CreateModelMixin, viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = models.OrgApplication.objects.all()
    permissions_classes = (IsAuthenticated,)
    serializer_class = serializers.OrgApplicationSerializer
    filterset_fields = ['status']

class JoinRequestViewSet(viewsets.mixins.UpdateModelMixin, viewsets.mixins.CreateModelMixin, viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = models.JoinRequest.objects.all()
    permissions_classes = (IsAuthenticated,)
    #serializer_class = serializers.JoinRequestSerializer
    filterset_fields = ['status', 'organization']

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.JoinRequestSerializerRead
        return serializers.JoinRequestSerializerWrite

class OrgMembersView(APIView):
    permission_classes = (IsAuthenticated,)
    invalid_org_response = Response(
                    {"message": "Invalid org_id parameter value"},
                    status=status.HTTP_400_BAD_REQUEST
                )
    not_org_admin_response = Response(
                    {"message": "You are not an org admin"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
    not_valid_user_id_response = Response(
                {"message": "Invalid user_id parameter value"},
                status=status.HTTP_400_BAD_REQUEST
            )
    """
    Get a list of members within the organization in two categroies: 
    Members and admin
    """
    def get(self, request, org_id):
        try:
            org = models.Organization.objects.get(id=org_id)
        except (models.Organization.DoesNotExist, ValueError):
            return self.invalid_org_response

        # check if the calling user is the org admin of the org
        org_role = request.user.userprofile.org_role
        if org_role is None or not (org_role.organization == org and org_role.is_admin == True):
            return self.not_org_admin_response
        
        admins = models.UserProfile.objects.filter(
            org_role__organization__exact=org_id, org_role__is_admin__exact=True)
        non_admin = models.UserProfile.objects.filter(
            org_role__organization__exact=org_id, org_role__is_admin__exact=False)
        admin_serializer = serializers.OrgMembersSerializer(admins, many=True)
        non_admin_serializer = serializers.OrgMembersSerializer(non_admin, many=True)

        data = {
            "members" : non_admin_serializer.data,
            "admins" : admin_serializer.data
        }

        return Response(data, status=status.HTTP_200_OK)

    """
    Add an user to the organization
    This endpoint should be only accessible to admins of the organization
    """
    def put(self, request, org_id):
        try:
            org = models.Organization.objects.get(id=org_id)
            user = User.objects.get(id=request.data.get('user_id'))
            user_profile = models.UserProfile.objects.get(user=user)
        except (models.Organization.DoesNotExist):
            return self.invalid_org_response
        except (models.User.DoesNotExist, models.UserProfile.DoesNotExist, ValueError):
            return self.not_valid_user_id_response
        
        # check if the calling user is the org admin of the org
        caller_org_role = request.user.userprofile.org_role
        if caller_org_role is None or not (caller_org_role.organization == org and caller_org_role.is_admin == True):
            return self.not_org_admin_response

        try:
            org_role = models.OrgRole.objects.get(organization=org, is_admin=request.data.get('is_admin'))
        except ValidationError:
            return Response(
                {"message": "org_role value must be either True or False."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # if everything is valid, update the org role in user profile
        user_profile.org_role = org_role
        user_profile.save()
        return Response(
            request.data,
            status=status.HTTP_201_CREATED)
    
    """
    Delete/remove an user from the organization
    This endpoint should be only be accessible to admins of the organization
    """
    def delete(self, request, org_id):
        try:
            org = models.Organization.objects.get(id=org_id)
            user = User.objects.get(id=request.data.get('user_id'))
            user_profile = models.UserProfile.objects.get(user=user)
        except (models.Organization.DoesNotExist):
            return self.invalid_org_response
        except (models.User.DoesNotExist, models.UserProfile.DoesNotExist, ValueError):
            return self.not_valid_user_id_response
        
        # check if the calling user is the org admin of the org
        org_role = request.user.userprofile.org_role
        if org_role is None or not (org_role.organization == org and org_role.is_admin == True):
            return self.not_org_admin_response

        # if everything is valid, update the org role in user profile
        user_profile.org_role = None
        user_profile.save()
        return Response(
            {"message": "user removed from org" + str(org.id)},
            status=status.HTTP_200_OK)
