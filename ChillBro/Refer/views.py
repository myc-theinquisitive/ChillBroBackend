from rest_framework import generics, status
from rest_framework.response import Response
from .models import ReferAndEarn
from .serializers import *
from .constants import SHARE_APP_MESSAGE
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient


# Create your views here.


class ReferBusinessClientList(generics.ListCreateAPIView):
    queryset = ReferBusinessClient.objects.all()
    serializer_class = ReferBusinessClientSerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient)


class ReferBusinessClientDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReferBusinessClient.objects.all()
    serializer_class = ReferBusinessClientSerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee,)


class ShareApp(APIView):
    def get(self, request):
        return Response({"message": SHARE_APP_MESSAGE})


class SignUpRequestCreate(generics.CreateAPIView):
    serializer_class = SignUpRequestSerialiser
    queryset = SignUpRequest.objects.all()


class SignUpRequestList(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    serializer_class = SignUpRequestSerialiser
    queryset = SignUpRequest.objects.all()

    def get(self, request, *args, **kwargs):
        self.queryset = SignUpRequest.objects.filter(status=kwargs['status'])
        return super().get(request, *args, **kwargs)


class SignUpRequestDetail(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    serializer_class = SignUpRequestApprovalSerialiser
    queryset = SignUpRequest.objects.all()


class GetUserReferAndEarnDetails(APIView):
    def get(self, request, *args, **kwargs):
        referals = ReferAndEarn.objects.select_related("referred_user").filter(referred_by=request.user)

        all_referal_details = []
        total_earnings = 0
        for referal in referals:
            total_earnings += referal.amount_earned
            referal_details = {
                "referred_user": referal.referred_user.first_name + " " + referal.referred_user.last_name,
                "amount": referal.amount_earned,
                "status": referal.status
            }
            all_referal_details.append(referal_details)

        response_data = {
            "refer_code": request.user.refer_code,
            "total_earnings": total_earnings,
            "referal_count": len(referals),
            "referals": all_referal_details
        }

        return Response(response_data, status=status.HTTP_200_OK)
