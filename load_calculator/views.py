from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LoadCalculation, LoadAppliance
from .serializers import LoadCalculationSerializer, LoadApplianceSerializer
import math

INSTALLATION_PERCENT = 0.12  # 12%

class LoadCalculationViewSet(viewsets.ModelViewSet):
    queryset = LoadCalculation.objects.select_related('customer')
    serializer_class = LoadCalculationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        customer_id = self.request.query_params.get('customer')
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        return qs.order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        appliances = request.data.get('appliances', [])
        
        total_watts = sum(int(a['watts']) * int(a['quantity']) for a in appliances)
        total_watt_hours = sum(
            int(a['watts']) * int(a['quantity']) * float(a['hours'])
            for a in appliances
        )
        
        # Inverter recommendation
        if total_watts <= 1000:
            inverter = "1.5KVA"
        elif total_watts <= 2000:
            inverter = "3.5KVA"
        elif total_watts <= 3500:
            inverter = "5KVA"
        elif total_watts <= 5000:
            inverter = "7.5KVA"
        else:
            inverter = "10KVA"
        
        # Battery recommendation (200Ah batteries at 12V)
        battery_count = math.ceil(total_watt_hours / (12 * 200))
        
        # Solar panel recommendation (350W panels, 5 hours sun)
        solar_panels = math.ceil(total_watt_hours / (5 * 350))
        
        return Response({
            'total_watts': total_watts,
            'total_watt_hours': total_watt_hours,
            'recommended_inverter': inverter,
            'recommended_battery_count': battery_count,
            'recommended_solar_panels': solar_panels,
            'appliances': appliances,
            # 'quotation_id': 1
        })