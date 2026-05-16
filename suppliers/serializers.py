from rest_framework import serializers
from .models import Supplier, PurchaseOrder, PurchaseOrderItem

class SupplierSerializer(serializers.ModelSerializer):
    total_orders = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = '__all__'
    
    def get_total_orders(self, obj):
        return obj.purchase_orders.count()
    
    def get_total_spent(self, obj):
        return sum(po.total_amount for po in obj.purchase_orders.filter(status='received'))

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.company_name', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'