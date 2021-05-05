from django.http import HttpResponse
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django.db.models import F
from .models import Wallet, WalletTransaction
from .serializers import WalletTransactionSerializer
from .constants import TransactionType
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


def add_amount(request):
    # wallet = Wallet.objects.get(created_by=request.user)
    # wallet.amount = F('amount') + request.data['amount']
    # wallet.save()
    wallet = Wallet.objects.filter(created_by=request.user)
    wallet.update(amount=F('amount') + request.data['amount'])


def deduct_amount(request):
    wallet = Wallet.objects.filter(created_by=request.user)
    if wallet[0].amount >= request.data['amount']:
        wallet.update(amount=F('amount') + request.data['amount'])
    else:
        raise ValidationError('No enough amount')


class GetAmount(APIView):
    def get(self, request):
        wallet = Wallet.objects.get(created_by=request.user.id)
        return Response(wallet.amount,200)


class WalletTransactions(generics.CreateAPIView):
    serializer_class = WalletTransactionSerializer
    queryset = Wallet.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request, type):
        request.data['created_by'] = request.user.id
        request.data[
            'transaction_type'] = TransactionType.CREDIT.value if type == TransactionType.CREDIT.value else TransactionType.DEBIT.value
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if type == TransactionType.CREDIT.value:
                add_amount(request)
            else:
                deduct_amount(request)
            serializer.save()
            return Response(serializer.data, 200)
        else:
            return Response(serializer.errors, 400)


class TransactionHistory(generics.ListAPIView):
    serializer_class = WalletTransactionSerializer
    queryset = WalletTransaction.objects.all()
    permission_classes = (IsAuthenticated,)

    def get(self, request,*args, **kwargs):
        self.queryset = WalletTransaction.objects.filter(created_by=request.user).order_by('-created_at', )
        return super().get(request, *args, **kwargs)