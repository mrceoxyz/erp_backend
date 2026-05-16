from rest_framework import serializers
from .models import Category, Product, StockAuditLog, ProductAudit

class StockAuditLogSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockAuditLog
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'

class ProductAuditSerializer(serializers.ModelSerializer):
    performed_by = serializers.StringRelatedField()

    class Meta:
        model = ProductAudit
        fields = [
            'id',
            'action',
            'previous_value',
            'new_value',
            'quantity',
            'performed_by',
            'created_at',
        ]