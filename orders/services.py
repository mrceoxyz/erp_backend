from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Order

@transaction.atomic
def cancel_order(order: Order):
    if order.status == Order.Status.CANCELLED:
        raise ValidationError("Order is already cancelled")

    # Restore stock
    for item in order.items.select_related("product"):
        product = item.product
        product.stock_quantity += item.quantity
        product.save(update_fields=["stock_quantity"])

    # Update order status
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])

    return order
