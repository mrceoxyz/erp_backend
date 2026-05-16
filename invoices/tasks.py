from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Invoice
from .pdf_generator import generate_invoice_pdf

@shared_task
def send_invoice_email(invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    customer = invoice.order.customer
    
    pdf_content = generate_invoice_pdf(invoice)
    
    subject = f'Invoice {invoice.invoice_number} from Solar Shop ERP'
    message = f"""
    Dear {customer.full_name},
    
    Please find attached your invoice #{invoice.invoice_number}.
    
    Invoice Details:
    - Total Amount: ₦{invoice.total_amount:,.2f}
    - Due Date: {invoice.due_date.strftime('%Y-%m-%d')}
    - Amount Paid: ₦{invoice.amount_paid:,.2f}
    - Balance Due: ₦{invoice.balance_due:,.2f}
    
    Thank you for your business!
    """
    
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [customer.email])
    email.attach(f'invoice_{invoice.invoice_number}.pdf', pdf_content, 'application/pdf')
    email.send()
    
    return f"Invoice email sent to {customer.email}"

@shared_task
def check_overdue_invoices():
    from django.utils import timezone
    
    overdue_invoices = Invoice.objects.filter(
        payment_status__in=['unpaid', 'partial'],
        due_date__lt=timezone.now().date()
    )
    
    for invoice in overdue_invoices:
        invoice.payment_status = 'overdue'
        invoice.save()
        
        customer = invoice.order.customer
        subject = f'Payment Reminder - Invoice {invoice.invoice_number}'
        message = f"""
        Dear {customer.full_name},
        
        Invoice #{invoice.invoice_number} is now overdue.
        Amount Due: ₦{invoice.balance_due:,.2f}
        Due Date: {invoice.due_date.strftime('%Y-%m-%d')}
        
        Please make payment at your earliest convenience.
        """
        
        email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [customer.email])
        email.send()
    
    return f"Checked {overdue_invoices.count()} overdue invoices"