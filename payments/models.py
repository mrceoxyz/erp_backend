from django.db import models

class Payment(models.Model):
    PAYMENT_METHOD = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('stripe', 'Stripe'),
        ('paystack', 'Paystack'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    invoice = models.ForeignKey('invoices.Invoice', on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_id = models.CharField(max_length=200, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"Payment {self.transaction_id}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'completed':
            invoice = self.invoice
            invoice.amount_paid = sum(
                p.amount for p in invoice.payments.filter(status='completed')
            )
            if invoice.amount_paid >= invoice.total_amount:
                invoice.payment_status = 'paid'
            elif invoice.amount_paid > 0:
                invoice.payment_status = 'partial'
            invoice.save()