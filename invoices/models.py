from django.db import models
from quotations.models import Quotation
from customers.models import Customer

class Invoice(models.Model):
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    # quotation = models.OneToOneField(Quotation, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=7.5)
    tax_amount = models.CharField(max_length=20)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    # @property
    # def balance_due(self):
    #     return self.total_amount - self.amount_paid