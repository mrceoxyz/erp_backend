from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.contrib.auth import get_user_model
from account.models import ShopAccount
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter as SearhchFilter
from rest_framework import filters
from supplier_order.models import SupplierPaymentAudit

User = get_user_model()

from .models import SupplierOrder
from .serializers import SupplierOrderSerializer
from products.models import Product
from django.db.models import F


class SupplierOrderViewSet(viewsets.ModelViewSet):
    queryset = SupplierOrder.objects.select_related("supplier").prefetch_related("items__product")
    serializer_class = SupplierOrderSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    search_fields = ['supplier__company_name', 'order_number']

    def list(self, request, *args, **kwargs):
        if request.query_params.get("all") == "true":
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        supplier = self.request.query_params.get('supplier')
        status_param = self.request.query_params.get('status')

        if supplier:
            qs = qs.filter(supplier_id=supplier)
        if status_param:
            qs = qs.filter(status=status_param)

        return qs.order_by('-created_at')

    @action(detail=True, methods=['patch'])
    @transaction.atomic
    def receive(self, request, pk=None):
        order = (
            SupplierOrder.objects
            .select_for_update()
            .prefetch_related("items__product")
            .select_related("supplier")
            .get(pk=pk)
        )

        if order.status == 'received':
            return Response(
                {'detail': 'Order already received'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate shop account
        account = ShopAccount.objects.select_for_update().first()
        if not account:
            return Response({'detail': 'Shop account not configured'}, status=500)
        if account.balance < order.total_amount:
            return Response({'detail': 'Insufficient funds in shop account'}, status=400)

        # Update stock
        for item in order.items.all():
            Product.objects.filter(pk=item.product_id).update(
                stock_quantity=F('stock_quantity') + item.quantity
            )

        # Store previous values for audit
        prev_total_spent = order.supplier.total_spent
        prev_balance = account.balance

        # Update supplier stats
        supplier = order.supplier
        supplier.total_orders = F('total_orders') + 1
        supplier.total_spent = F('total_spent') + order.total_amount
        supplier.save(update_fields=['total_orders', 'total_spent'])

        # Update shop account balance
        account.balance = F('balance') - order.total_amount
        account.save(update_fields=['balance'])

        # Mark order as received
        order.status = 'received'
        order.save(update_fields=['status'])

        # Create audit trail
        SupplierPaymentAudit.objects.create(
            supplier=supplier,
            order_number=order.order_number,
            previous_total_spent=prev_total_spent,
            new_total_spent=prev_total_spent + order.total_amount,
            amount=order.total_amount,
            processed_by=request.user if request.user.is_authenticated else None,
            shop_account_balance_before=prev_balance,
            shop_account_balance_after=prev_balance - order.total_amount,
        )

        return Response({'detail': 'Order received successfully'})

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        from .utils import generate_purchase_order_pdf
        order = self.get_object()
        return generate_purchase_order_pdf(order)
    
    @action(detail=False, methods=['get'], url_path='supplier-payments')
    def supplier_payments(self, request):
        """
        Returns supplier payment audit records.
        """
        from .models import SupplierPaymentAudit  # your audit model
        from .serializers import SupplierPaymentAuditSerializer

        audits = SupplierPaymentAudit.objects.select_related('supplier').order_by('-created_at')
        serializer = SupplierPaymentAuditSerializer(audits, many=True)
        return Response({'results': serializer.data})