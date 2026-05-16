from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils.timezone import now

from .models import Quotation
from .serializers import QuotationSerializer
from products.models import Product
from invoices.models import Invoice
from load_calculator.models import LoadCalculation


class QuotationViewSet(viewsets.ModelViewSet):
    queryset = Quotation.objects.select_related(
        'customer', 'inverter', 'battery', 'solar_panel'
    )
    serializer_class = QuotationSerializer

    @action(detail=False, methods=['post'], url_path='from-load')
    @transaction.atomic
    def from_load(self, request):
        load_id = request.data.get('load_calculation_id')

        load = LoadCalculation.objects.select_related('customer').get(id=load_id)

        inverter = Product.objects.filter(
            category__name__icontains='inverter',
            capacity__gte=load.recommended_inverter
        ).order_by('price').first()

        battery = Product.objects.filter(
            category__name__icontains='battery'
        ).order_by('price').first()

        panel = Product.objects.filter(
            category__name__icontains='panel'
        ).order_by('price').first()

        installation_cost = 0.1 * (
            inverter.price +
            battery.price * load.recommended_battery_count +
            panel.price * load.recommended_solar_panels
        )

        subtotal = (
            inverter.price +
            battery.price * load.recommended_battery_count +
            panel.price * load.recommended_solar_panels +
            installation_cost
        )

        quotation = Quotation.objects.create(
            quotation_number=f"Q-{now().strftime('%Y%m%d%H%M%S')}",
            customer=load.customer,
            load_calculation=load,
            inverter=inverter,
            battery=battery,
            solar_panel=panel,
            battery_quantity=load.recommended_battery_count,
            panel_quantity=load.recommended_solar_panels,
            installation_cost=installation_cost,
            subtotal=subtotal,
            total=subtotal,
        )

        return Response(
            QuotationSerializer(quotation).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def convert_to_invoice(self, request, pk=None):
        quotation = self.get_object()

        if quotation.status != 'pending':
            return Response(
                {'detail': 'Quotation already processed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        invoice = Invoice.objects.create(
            customer=quotation.customer,
            total_amount=quotation.total,
            reference=quotation.quotation_number
        )

        quotation.status = 'converted'
        quotation.save(update_fields=['status'])

        return Response({'invoice_id': invoice.id})
