from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse

def generate_quotation_pdf(quotation):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={quotation.quotation_number}.pdf'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph(f"<b>Quotation:</b> {quotation.quotation_number}", styles['Title']))
    content.append(Paragraph(f"Customer: {quotation.customer.full_name}", styles['Normal']))
    content.append(Paragraph(f"Inverter: {quotation.inverter}", styles['Normal']))
    content.append(Paragraph(f"Battery: {quotation.battery}", styles['Normal']))
    content.append(Paragraph(f"Solar Panels: {quotation.panel_quantity} × {quotation.solar_panel}", styles['Normal']))
    content.append(Paragraph(f"Installation: ₦{quotation.installation_cost}", styles['Normal']))
    content.append(Paragraph(f"<b>Total: ₦{quotation.total}</b>", styles['Heading2']))

    doc.build(content)
    return response
