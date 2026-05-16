from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from .models import Invoice
from .serializers import InvoiceSerializer
from .pdf_generator import generate_invoice_pdf
from .tasks import send_invoice_email

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("order")
    serializer_class = InvoiceSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]

    search_fields = [
        'invoice_number',
        'order__customer__first_name',
        'order__customer__last_name',
    ]

    filterset_fields = {
        "payment_status": ["exact"],   # paid / unpaid / overdue / partial 
    }

    def list(self, request, *args, **kwargs):
        if request.query_params.get("all") == "true":
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        invoice = self.get_object()
        pdf_content = generate_invoice_pdf(invoice)
        
        response = FileResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        return response
    
    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        invoice = self.get_object()
        send_invoice_email.delay(invoice.id)
        return Response({'message': 'Invoice email queued for sending'})

