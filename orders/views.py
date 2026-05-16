from rest_framework import viewsets, status
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Order, OrderHistory
from .serializers import OrderSerializer, OrderHistorySerializer, OrderListSerializer
from .utils import adjust_stock_for_order, update_order_items_with_diff

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "customer__first_name",
        "customer__last_name",
        "order_number",
    ]

    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        with transaction.atomic():
            order = serializer.save()
            adjust_stock_for_order(order, action='create', user=self.request.user)
            
            # Create history entry
            OrderHistory.objects.create(
                order=order,
                action='order_created',
                changes={'status': 'created'},
                performed_by=self.request.user,
                notes=f"Order {order.order_number} created"
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        '''Cancel order and restock items'''
        order = self.get_object()
        
        if order.status == 'cancelled':
            return Response(
                {'error': 'Order is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if order.status == 'completed':
            return Response(
                {'error': 'Cannot cancel completed order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            previous_status = order.status
            order.status = 'cancelled'
            order.save()
            
            # Restock items
            adjust_stock_for_order(order, action='cancel', user=request.user)
            
            # Create history entry
            OrderHistory.objects.create(
                order=order,
                action='order_cancelled',
                changes={
                    'status': {'from': previous_status, 'to': 'cancelled'},
                    'restocked': True
                },
                performed_by=request.user,
                notes=request.data.get('reason', 'Order cancelled and items restocked')
            )
        
        return Response({
            'message': 'Order cancelled and items restocked successfully',
            'order': OrderSerializer(order).data
        })
    
    @action(detail=True, methods=['patch'])
    def update_items(self, request, pk=None):
        '''Update order items with diff-based approach'''
        order = self.get_object()
        
        if order.status in ['completed', 'cancelled']:
            return Response(
                {'error': f'Cannot modify {order.status} order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_items_data = request.data.get('items', [])
        
        with transaction.atomic():
            changes = update_order_items_with_diff(
                order, 
                new_items_data, 
                user=request.user
            )
            
            # Recalculate total
            order.total_amount = sum(item.subtotal for item in order.items.all())
            order.save()
        
        return Response({
            'message': 'Order items updated successfully',
            'changes': changes,
            'order': OrderSerializer(order).data
        })
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        '''Get order history'''
        order = self.get_object()
        history = order.history.all()
        serializer = OrderHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def audit_trail(self, request, pk=None):
        '''Get stock audit trail for order'''
        from products.models import StockAuditLog
        from products.serializers import StockAuditLogSerializer
        
        order = self.get_object()
        audits = StockAuditLog.objects.filter(reference_order=order)
        serializer = StockAuditLogSerializer(audits, many=True)
        return Response(serializer.data)