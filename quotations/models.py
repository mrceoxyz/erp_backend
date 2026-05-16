from django.db import models
from customers.models import Customer
from products.models import Product

class Quotation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('converted', 'Converted to Invoice'),
    )

    quotation_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    load_calculation = models.OneToOneField(
        'load_calculator.LoadCalculation',
        on_delete=models.CASCADE,
        related_name='quotation'
    )

    inverter = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='inverter_quotes')
    battery = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='battery_quotes')
    solar_panel = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='panel_quotes')

    battery_quantity = models.PositiveIntegerField()
    panel_quantity = models.PositiveIntegerField()

    installation_cost = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.quotation_number
