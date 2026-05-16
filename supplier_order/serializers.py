from rest_framework import serializers
from .models import SupplierOrder, SupplierOrderItem, SupplierPaymentAudit
from products.models import Product


class SupplierOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = SupplierOrderItem
        fields = (
            'product',
            'product_name',
            'quantity',
            'unit_cost',
            'subtotal',
        )


class SupplierOrderSerializer(serializers.ModelSerializer):
    items = SupplierOrderItemSerializer(many=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.company_name')

    class Meta:
        model = SupplierOrder
        fields = (
            'id',
            'order_number',
            'supplier',
            'supplier_name',
            'status',
            'total_amount',
            'items',
            'created_at',
        )
        read_only_fields = ('order_number', 'total_amount')
    
    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError(
                "At least one order item is required."
            )

        for index, item in enumerate(items):
            if not item.get('product'):
                raise serializers.ValidationError(
                    f"Item #{index + 1}: Product is required."
                )

            if item.get('quantity', 0) <= 0:
                raise serializers.ValidationError(
                    f"Item #{index + 1}: Quantity must be greater than zero."
                )

            if item.get('unit_cost', 0) <= 0:
                raise serializers.ValidationError(
                    f"Item #{index + 1}: Unit cost must be greater than zero."
                )

        return items

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        order = SupplierOrder.objects.create(
            **validated_data,
            order_number=f"PO-{SupplierOrder.objects.count()+1:06d}"
        )

        total = 0
        for item in items_data:
            product = item['product']
            quantity = item['quantity']
            unit_cost = item['unit_cost']

            subtotal = quantity * unit_cost
            total += subtotal

            SupplierOrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_cost=unit_cost,
                subtotal=subtotal,
            )

        order.total_amount = total
        order.save()
        return order

class SupplierPaymentAuditSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.company_name', read_only=True)
    processed_by = serializers.CharField(source='processed_by.username', read_only=True)

    class Meta:
        model = SupplierPaymentAudit
        fields = '__all__'