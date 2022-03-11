from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django.db.models import F, Q, Sum
from .models import Wallet, WalletTransaction
from .serializers import WalletTransactionSerializer
from .constants import TransactionType
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status


def get_amount_earned_for_related_ids(related_ids):
    return WalletTransaction.objects.filter(
        Q(related_id__in=related_ids) & Q(transaction_type=TransactionType.CREDIT.value))\
        .values('related_id').annotate(earned_amount=Sum('amount')).values('related_id', 'earned_amount')


def add_amount(user, amount):
    wallet = Wallet.objects.filter(created_by=user)
    wallet.update(amount=F('amount') + amount)


def deduct_amount(user, amount):
    wallet = Wallet.objects.filter(created_by=user)
    if wallet[0].amount >= amount:
        wallet.update(amount=F('amount') - amount)
    else:
        raise ValidationError('No enough amount')


class GetAmount(APIView):
    def get(self, request):
        try:
            wallet = Wallet.objects.get(created_by=request.user.id)
        except ObjectDoesNotExist:
            return Response(data={"errors": "Wallet not present"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"amount": wallet.amount}, status=status.HTTP_200_OK)


# TODO: This need not be exposed outside
class WalletTransactions(generics.CreateAPIView):
    serializer_class = WalletTransactionSerializer
    queryset = Wallet.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request, type):
        request.data['created_by'] = request.user.id
        # TODO: is this statement required??
        request.data['transaction_type'] = TransactionType.CREDIT.value \
            if type == TransactionType.CREDIT.value else TransactionType.DEBIT.value
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if type == TransactionType.CREDIT.value:
                add_amount(request.user, request.data['amount'])
            else:
                deduct_amount(request.user, request.data['amount'])
            serializer.save()
            return Response(serializer.data, 200)
        else:
            return Response(serializer.errors, 400)


class TransactionHistory(generics.ListAPIView):
    serializer_class = WalletTransactionSerializer
    queryset = WalletTransaction.objects.all()
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        self.queryset = WalletTransaction.objects.filter(created_by=request.user)
        if kwargs["type"] == "CREDIT":
            self.queryset = self.queryset.filter(transaction_type=TransactionType.CREDIT.value)
        elif kwargs["type"] == "DEBIT":
            self.queryset = self.queryset.filter(transaction_type=TransactionType.DEBIT.value)
        self.queryset = self.queryset.order_by('-created_at', )
        return super().get(request, *args, **kwargs)
