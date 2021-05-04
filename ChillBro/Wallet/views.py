from django.http import HttpResponse
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from .models import Wallet, WalletTransaction
from .serializers import WalletTransactionSerializer
from .constants import Types
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

def add_amount(request):
    wallet = Wallet.objects.get(user=request.user)
    wallet.amount += request.data['amount']
    wallet.save()

def deduct_amount(request):
    wallet = Wallet.objects.get(user=request.user)
    if wallet.amount>request.data['amount']:
        wallet.amount -= request.data['amount']
        wallet.save()
    else:
        raise ValidationError('No enough amount')


class GetAmount(APIView):
    def get(self, request):
        wallet = Wallet.objects.get(user=request.user.id)
        return HttpResponse(wallet.amount)


class WalletTransactions(generics.CreateAPIView):
    serializer_class = WalletTransactionSerializer
    queryset = Wallet.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request,type):
        request.data['user'] = request.user.id
        request.data['transaction_type'] = Types.CREDIT.value if type == Types.CREDIT.value else Types.DEBIT.value
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if type == Types.CREDIT.value:
                add_amount(request)
            else:
                deduct_amount(request)
            serializer.save()
            return Response(serializer.data,200)
        else:
            return Response(serializer.errors,400)


class TransactionHistory(generics.ListAPIView):
    serializer_class = WalletTransactionSerializer
    queryset = WalletTransaction.objects.all()
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        transactions = WalletTransaction.objects.filter(user=request.user).order_by('-created_at',)
        serializer = self.serializer_class(transactions,many=True)
        return Response(serializer.data,200)