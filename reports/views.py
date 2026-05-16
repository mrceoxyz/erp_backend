from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from products.models import Product
from customers.models import Customer
from invoices.models import Invoice
from payments.models import Payment
from suppliers.models import Supplier
from supplier_order.models import SupplierPaymentAudit
from supplier_order.serializers import SupplierPaymentAuditSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class ReportsViewSet(APIView):

    @action(detail=False, methods=['get'])
    def supplier_payments(self, request):
        period = request.query_params.get('period', 'month')
        supplier = request.query_params.get('supplier')

        queryset = SupplierPaymentAudit.objects.all()
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        # Optionally filter by period (day/week/month/etc)
        # Implement period filter logic here

        serializer = SupplierPaymentAuditSerializer(queryset.order_by('-created_at'), many=True)
        return Response({'results': serializer.data})


class SalesReportView(APIView):
    def get(self, request):
        period = request.query_params.get('period', 'month')
        
        if period == 'day':
            start_date = timezone.now().date()
        elif period == 'week':
            start_date = timezone.now().date() - timedelta(days=7)
        elif period == 'month':
            start_date = timezone.now().date() - timedelta(days=30)
        else:
            start_date = timezone.now().date() - timedelta(days=365)
        
        orders = Order.objects.filter(created_at__gte=start_date)
        
        total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_orders = orders.count()
        
        category_sales = OrderItem.objects.filter(
            order__created_at__gte=start_date
        ).values('product__category__name').annotate(
            total=Sum(F('quantity') * F('unit_price'))
        ).order_by('-total')
        
        top_products = OrderItem.objects.filter(
            order__created_at__gte=start_date
        ).values('product__name').annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('unit_price'))
        ).order_by('-quantity_sold')[:10]
        
        return Response({
            'period': period,
            'total_sales': total_sales,
            'total_orders': total_orders,
            'average_order_value': total_sales / total_orders if total_orders > 0 else 0,
            'category_sales': list(category_sales),
            'top_products': list(top_products)
        })

class InventoryReportView(APIView):
    def get(self, request):
        total_products = Product.objects.count()
        total_value = Product.objects.aggregate(
            total=Sum(F('stock_quantity') * F('price'))
        )['total'] or 0
        
        low_stock = Product.objects.filter(
            stock_quantity__lte=F('reorder_level')
        ).count()
        
        out_of_stock = Product.objects.filter(stock_quantity=0).count()
        
        category_stock = Product.objects.values('category__name').annotate(
            total_quantity=Sum('stock_quantity'),
            total_value=Sum(F('stock_quantity') * F('price'))
        )
        
        return Response({
            'total_products': total_products,
            'total_inventory_value': total_value,
            'low_stock_items': low_stock,
            'out_of_stock_items': out_of_stock,
            'category_breakdown': list(category_stock)
        })

class CustomerReportView(APIView):
    def get(self, request):
        total_customers = Customer.objects.count()
        
        top_customers = Customer.objects.annotate(
            total_spent=Sum('orders__total_amount'),
            order_count=Count('orders')
        ).order_by('-total_spent')[:10]
        
        start_of_month = timezone.now().replace(day=1)
        new_customers = Customer.objects.filter(created_at__gte=start_of_month).count()
        
        customer_data = [{
            'name': c.full_name,
            'total_spent': c.total_spent or 0,
            'order_count': c.order_count
        } for c in top_customers]
        
        return Response({
            'total_customers': total_customers,
            'new_customers_this_month': new_customers,
            'top_customers': customer_data
        })

class FinancialReportView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            invoices = Invoice.objects.filter(
                issue_date__gte=start_date,
                issue_date__lte=end_date
            )
            payments = Payment.objects.filter(
                payment_date__gte=start_date,
                payment_date__lte=end_date,
                status='completed'
            )
        else:
            invoices = Invoice.objects.all()
            payments = Payment.objects.filter(status='completed')
        
        total_invoiced = invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        outstanding = invoices.filter(
            payment_status__in=['unpaid', 'partial', 'overdue']
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        payment_methods = payments.values('payment_method').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        return Response({
            'total_invoiced': total_invoiced,
            'total_collected': total_paid,
            'outstanding_amount': outstanding,
            'payment_by_method': list(payment_methods)
        })

class SupplierReportView(APIView):
    def get(self, request):
        suppliers = Supplier.objects.annotate(
            total_orders=Count('purchase_orders'),
            total_spent=Sum('purchase_orders__total_amount')
        ).order_by('-total_spent')[:10]
        
        supplier_data = [{
            'name': s.company_name,
            'total_orders': s.total_orders,
            'total_spent': s.total_spent or 0
        } for s in suppliers]
        
        return Response({
            'top_suppliers': supplier_data
        })
