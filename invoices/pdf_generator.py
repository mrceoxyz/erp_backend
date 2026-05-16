from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO

def generate_invoice_pdf(invoice):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("INVOICE", title_style))
    elements.append(Spacer(1, 12))
    
    # Company Info
    company_info = [
        ["Solar Shop ERP", ""],
        ["123 Business Street", f"Invoice #: {invoice.invoice_number}"],
        ["Lagos, Nigeria", f"Date: {invoice.issue_date.strftime('%Y-%m-%d')}"],
        ["Phone: +234 800 000 0000", f"Due Date: {invoice.due_date.strftime('%Y-%m-%d')}"],
    ]
    
    company_table = Table(company_info, colWidths=[3*inch, 3*inch])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 20))
    
    # Customer Info
    customer = invoice.order.customer
    bill_to = Paragraph(f"<b>Bill To:</b><br/>{customer.full_name}<br/>"
                        f"{customer.address}<br/>{customer.city}, {customer.state}<br/>"
                        f"Phone: {customer.phone}", styles['Normal'])
    elements.append(bill_to)
    elements.append(Spacer(1, 20))
    
    # Items Table
    data = [['Item', 'Quantity', 'Unit Price', 'Total']]
    for item in invoice.order.items.all():
        data.append([
            item.product.name,
            str(item.quantity),
            f"₦{item.unit_price:,.2f}",
            f"₦{item.subtotal:,.2f}"
        ])
    
    # Add totals
    data.append(['', '', 'Subtotal:', f"₦{invoice.subtotal:,.2f}"])
    data.append(['', '', f'Tax ({invoice.tax_rate}%):', f"₦{invoice.tax_amount:,.2f}"])
    if invoice.discount > 0:
        data.append(['', '', 'Discount:', f"-₦{invoice.discount:,.2f}"])
    data.append(['', '', 'Total:', f"₦{invoice.total_amount:,.2f}"])
    data.append(['', '', 'Amount Paid:', f"₦{invoice.amount_paid:,.2f}"])
    data.append(['', '', 'Balance Due:', f"₦{invoice.balance_due:,.2f}"])
    
    table = Table(data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -7), colors.beige),
        ('GRID', (0, 0), (-1, -7), 1, colors.black),
        ('LINEABOVE', (2, -6), (-1, -6), 1, colors.black),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    if invoice.notes:
        notes = Paragraph(f"<b>Notes:</b><br/>{invoice.notes}", styles['Normal'])
        elements.append(notes)
    
    elements.append(Spacer(1, 30))
    footer = Paragraph("Thank you for your business!", 
                       ParagraphStyle('Footer', parent=styles['Normal'], 
                                      alignment=TA_CENTER, fontSize=10))
    elements.append(footer)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf