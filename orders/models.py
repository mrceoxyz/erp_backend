from django.db import models
from customers.models import Customer
from products.models import Product

class OrderHistory(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=50)
    changes = models.JSONField(default=dict)
    performed_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.action} - {self.timestamp}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CANCELLED = 'cancelled', 'Cancelled'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        DRAFT = 'draft', 'Draft'
        # ... other choices ...

    # STATUS_CHOICES = [
    #     (DRAFT, "Draft"),
    #     ("pending", "Pending"),
    #     ("processing", "Processing"),
    #     ("completed", "Completed"),
    #     ("cancelled", "Cancelled"),
    # ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"