from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework import status
from identity.models import Organization
from listing.models import Donation, Request
from listing.serializers import DonationSerializer, RequestSerializer
from datetime import datetime
from django.utils import timezone

class DonationView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **kwargs):
        org_id = request.query_params.get('org_id', None)
        donation_status = request.query_params.get('status', None)
        all_donations = Donation.objects.all()
        donations_filtered = all_donations
        if org_id is not None:
            try:
                org = Organization.objects.get(id=org_id)
            except (Organization.DoesNotExist, ValueError):
                return Response(
                    {"message": "Invalid org_id parameter value"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            donations_filtered = all_donations.filter(organization=org)

        if donation_status is not None:
            # validate if the status is in "active" or "inactive"
            if donation_status not in ["active", "inactive"]:
                return Response(
                    {"message": "Invalid status parameter value"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if donation_status == "active":
                donations_filtered = donations_filtered.exclude(deactivation_time__lte=datetime.now(tz=timezone.utc))
            elif donation_status == "inactive":
                donations_filtered = donations_filtered.filter(deactivation_time__lte=datetime.now(tz=timezone.utc))

        # if query set emtpy 
        if not donations_filtered:
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = DonationSerializer(donations_filtered, many=True)
        return Response(
                    {"donations": serializer.data},
                    status=status.HTTP_200_OK
                )
        
    def post(self, request, format=None):
        serializer = DonationSerializer(data=request.data)
        if serializer.is_valid():
            created_donation = serializer.save()
            return Response({"donation_id": created_donation.donation_id}, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        key = list(errors.keys())[0]
        return Response(
            {"message": "for key " + key + " "+  str(errors[key])},
            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        donation_id = request.data.get('donation_id', None)
        if donation_id is not None:
            try:
                donation = Donation.objects.get(donation_id=donation_id)
            except (Donation.DoesNotExist, ValueError):
                return Response(
                    {"message": "Invalid org_id parameter value"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = DonationSerializer(donation)
            # soft_delete will be triggered in save()
            serializer.save()
            return Response(status=status.HTTP_200_OK)

class RequestView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None, **kwargs):
        org_id = request.query_params.get('org_id', None)
        request_status = request.query_params.get('status', None)
        all_requests = Request.objects.all()
        requests_filtered = all_requests
        if org_id is not None:
            try:
                org = Organization.objects.get(id=org_id)
            except (Organization.DoesNotExist, ValueError):
                return Response(
                    {"message": "Invalid org_id parameter value"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            requests_filtered = all_requests.filter(organization=org)

        if request_status is not None:
            # validate if the status is in "active" or "inactive"
            if request_status not in ["active", "inactive"]:
                return Response(
                    {"message": "Invalid status parameter value"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if request_status == "active":
                requests_filtered = requests_filtered.exclude(deactivation_time__lte=datetime.now(tz=timezone.utc))
            elif request_status == "inactive":
                requests_filtered = requests_filtered.filter(deactivation_time__lte=datetime.now(tz=timezone.utc))

        # if query set emtpy 
        if not requests_filtered:
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = RequestSerializer(requests_filtered, many=True)
        return Response(
                    {"requests": serializer.data},
                    status=status.HTTP_200_OK
                )
    def post(self, request, format=None):
        serializer = RequestSerializer(data=request.data)
        if serializer.is_valid():
            created_request = serializer.save()
            return Response(
                {"request_id": created_request.request_id},
                 status=status.HTTP_201_CREATED)
        errors = serializer.errors
        key = list(errors.keys())[0]
        return Response(
            {"message": "for key " + key + " "+  str(errors[key])},
            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        request_id = request.data.get('request_id', None)
        if request_id is not None:
            try:
                request = Request.objects.get(request_id=request_id)
            except (Request.DoesNotExist, ValueError):
                return Response(
                    {"message": "Invalid org_id parameter value"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RequestSerializer(request)
            # soft_delete will be triggered in save()
            serializer.save()
            return Response(status=status.HTTP_200_OK)

