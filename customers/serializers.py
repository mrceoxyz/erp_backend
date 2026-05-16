from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    total_orders = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = '__all__'
    
    def get_total_orders(self, obj):
        return obj.orders.count()
    
    def get_total_spent(self, obj):
        return sum(order.total_amount for order in obj.orders.all())