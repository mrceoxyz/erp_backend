from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'phone', 'city', 'is_active']
    list_filter = ['is_active', 'state']
    search_fields = ['company_name', 'email']

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'status', 'total_amount', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['po_number']
    inlines = [PurchaseOrderItemInline]