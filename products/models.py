from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class StockReservation(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quotation = models.ForeignKey(
        "quotations.Quotation",
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    quantity = models.PositiveIntegerField()
    reserved_at = models.DateTimeField(auto_now_add=True)

class StockAuditLog(models.Model):
    ACTION_TYPES = [
        ('order_created', 'Order Created'),
        ('order_cancelled', 'Order Cancelled'),
        ('order_updated', 'Order Updated'),
        ('manual_adjustment', 'Manual Adjustment'),
        ('purchase_received', 'Purchase Received'),
    ]
    
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='stock_audits')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    quantity_change = models.IntegerField()  # Positive for increase, negative for decrease
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reference_order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.action_type} - {self.quantity_change}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    specifications = models.JSONField(default=dict, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    
    def __str__(self):
        return self.name
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level
    

class ProductAudit(models.Model):
    ACTION_CHOICES = (
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('stock_in', 'Stock In'),
        ('stock_out', 'Stock Out'),
        ('price_change', 'Price Change'),
    )

    product = models.ForeignKey(
        'products.Product',
        related_name='audits',
        on_delete=models.CASCADE
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    previous_value = models.CharField(max_length=255, blank=True, null=True)
    new_value = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)

    performed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.name} - {self.action}'
