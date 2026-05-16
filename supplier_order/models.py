from django.db import models
from django.utils import timezone
from products.models import Product
from suppliers.models import Supplier


class SupplierOrder(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    )

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name='orders'
    )
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ordered'
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.order_number


class SupplierOrderItem(models.Model):
    order = models.ForeignKey(
        SupplierOrder, on_delete=models.CASCADE, related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

class SupplierPaymentAudit(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payment_audits')
    order_number = models.CharField(max_length=100)
    previous_total_spent = models.DecimalField(max_digits=12, decimal_places=2)
    new_total_spent = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    processed_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True)
    shop_account_balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    shop_account_balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Audit: {self.supplier} - {self.amount} ({self.order_number})"
