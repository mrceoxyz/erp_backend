from rest_framework import serializers
from .models import Order, OrderHistory, OrderItem


class OrderItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("product", "quantity", "unit_price", "subtotal")


class OrderItemReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "subtotal",
        )


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.full_name",
        read_only=True
    )
    items = OrderItemWriteSerializer(many=True, write_only=True)
    order_items = OrderItemReadSerializer(
        source="items", many=True, read_only=True
    )

    class Meta:
        model = Order
        fields = "__all__"

    def create(self, validated_data):
        items_data = validated_data.pop("items")

        order = Order.objects.create(**validated_data)

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                **item
            )
            for item in items_data
        ])

        return order

class OrderHistorySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(
        source="performed_by.get_full_name",
        read_only=True
    )

    class Meta:
        model = OrderHistory
        fields = "__all__"

class OrderListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.full_name",
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "customer_name",
            "status",
            "total_amount",
            "created_at",
        ]