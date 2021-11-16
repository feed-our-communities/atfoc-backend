from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from identity.models import Organization, OrgStatus, UserProfile, OrgRole
from listing.models import Donation
from listing.serializers import DonationsSerializer
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

        serializer = DonationsSerializer(donations_filtered, many=True)
        
        return Response(
                    {"donations": serializer.data},
                    status=status.HTTP_200_OK
                )
        


