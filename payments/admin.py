from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'invoice', 'payment_method', 'amount', 'status', 'payment_date']
    list_filter = ['payment_method', 'status', 'payment_date']
    search_fields = ['transaction_id', 'reference_number']