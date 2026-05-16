from django.contrib import admin
from .models import LoadCalculation, LoadAppliance

class LoadApplianceInline(admin.TabularInline):
    model = LoadAppliance
    extra = 1

@admin.register(LoadCalculation)
class LoadCalculationAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'total_watts', 'total_watt_hours', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    inlines = [LoadApplianceInline]