from rest_framework import serializers
from .models import LoadCalculation, LoadAppliance

class LoadApplianceSerializer(serializers.ModelSerializer):
    daily_consumption = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = LoadAppliance
        fields = '__all__'

class LoadCalculationSerializer(serializers.ModelSerializer):
    appliances = LoadApplianceSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = LoadCalculation
        fields = '__all__'

    def get_quotation_id(self, obj):
        return getattr(obj.quotation, 'id', None)