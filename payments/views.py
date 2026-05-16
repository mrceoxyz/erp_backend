from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
import stripe
import requests
from .models import Payment
from .serializers import PaymentSerializer
from account.models import ShopAccount

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("invoice")
    serializer_class = PaymentSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]  # Add your filter backends here
    # pagination_class = None  # Disable pagination for simplicity

    search_fields = [
        'transaction_id',
        'invoice__invoice_number',
        'invoice__order__customer__first_name',
    ]

     # filter by status
    filterset_fields = {
        "status": ["exact"],   # completed / pending / failed
    }

    def list(self, request, *args, **kwargs):
        if request.query_params.get("all") == "true":
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        with transaction.atomic():
            payment = serializer.save()
            invoice = payment.invoice
            order = invoice.order  # assuming one invoice per order

            # Update invoice balance
            # invoice.balance_due -= payment.amount
            # if invoice.balance_due <= 0:
            #     invoice.balance_due = 0
            #     invoice.status = 'completed'
            #     order.status = 'paid'
            # else:
            #     invoice.status = 'partial'

            account = ShopAccount.objects.first()
            if not account:
                return Response(
                    {'detail': 'Shop account not configured'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            account.balance += payment.amount
            account.save()

            order.status = 'paid'
            payment.status = 'completed'
            payment.save()
            invoice.status = 'completed'
            invoice.save()
            order.save()

            # Deduct stock for each item in order
            for item in order.items.all():
                product = item.product
                product.stock_quantity -= item.quantity
                if product.stock_quantity < 0:
                    product.stock_quantity = 0
                product.save()
    
    @action(detail=False, methods=['post'])
    def process_stripe(self, request):
        try:
            amount = int(float(request.data['amount']) * 100)
            invoice_id = request.data['invoice_id']
            
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='ngn',
                metadata={'invoice_id': invoice_id}
            )
            
            return Response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def process_paystack(self, request):
        try:
            url = 'https://api.paystack.co/transaction/initialize'
            headers = {
                'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'email': request.data['email'],
                'amount': int(float(request.data['amount']) * 100),
                'reference': request.data.get('reference'),
                'metadata': {'invoice_id': request.data['invoice_id']}
            }
            
            response = requests.post(url, json=data, headers=headers)
            return Response(response.json())
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
