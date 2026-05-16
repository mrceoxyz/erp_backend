from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse


def generate_purchase_order_pdf(order):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{order.order_number}.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "PURCHASE ORDER")
    y -= 30

    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, y, f"PO Number: {order.order_number}")
    y -= 15
    pdf.drawString(40, y, f"Supplier: {order.supplier.company_name}")
    y -= 15
    pdf.drawString(40, y, f"Date: {order.created_at.strftime('%Y-%m-%d')}")
    y -= 30

    pdf.drawString(40, y, "Products:")
    y -= 20

    pdf.drawString(40, y, "Product")
    pdf.drawString(260, y, "Qty")
    pdf.drawString(310, y, "Unit Cost")
    pdf.drawString(400, y, "Subtotal")
    y -= 15

    for item in order.items.all():
        pdf.drawString(40, y, item.product.name)
        pdf.drawString(260, y, str(item.quantity))
        pdf.drawString(310, y, f"{item.unit_cost}")
        pdf.drawString(400, y, f"{item.subtotal}")
        y -= 15

    y -= 20
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, f"Total: {order.total_amount}")

    pdf.showPage()
    pdf.save()
    return response
