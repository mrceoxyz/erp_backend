from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'order', 'payment_status', 'total_amount', 'balance_due', 'due_date']
    list_filter = ['payment_status', 'issue_date']
    search_fields = ['invoice_number', 'order__order_number']
    readonly_fields = ['balance_due']
