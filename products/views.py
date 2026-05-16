# from requests import request
from rest_framework import viewsets, filters, request
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, F
from .models import Category, Product, StockAuditLog
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CategorySerializer, ProductSerializer, StockAuditLogSerializer, ProductAuditSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]

    search_fields = ["name", "sku", "category__name"]

    filterset_fields = {
        "category": ["exact"],
    }

    ordering_fields = ["name", "stock"]
    ordering = ["name"]

    def list(self, request, *args, **kwargs):
        if request.query_params.get("low_stock") == "true":
            self.queryset = self.queryset.filter(
                stock__lte=F("low_stock_threshold")
            )

        if request.query_params.get("all") == "true":
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        return super().list(request, *args, **kwargs)

    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        low_stock_products = [p for p in self.queryset if p.is_low_stock]
        serializer = self.get_serializer(low_stock_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_id = request.query_params.get('category_id')
        if category_id:
            products = self.queryset.filter(category_id=category_id)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        return Response({'error': 'category_id parameter required'}, status=400)
    

    @action(detail=True, methods=['get'])
    def audit_logs(self, request, pk=None):
        '''Get audit logs for a product'''
        product = self.get_object()
        logs = product.stock_audits.all()[:50]  # Last 50 entries
        serializer = StockAuditLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent_changes(self, request):
        '''Get recent stock changes across all products'''
        logs = StockAuditLog.objects.all()[:100]
        serializer = StockAuditLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='audit')
    def audit(self, request, pk=None):
        product = self.get_object()
        audits = product.audits.select_related('performed_by')
        serializer = ProductAuditSerializer(audits, many=True)
        return Response({'results': serializer.data})