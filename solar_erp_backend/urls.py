from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import CustomTokenObtainPairView, AuthViewSet
from products.views import CategoryViewSet, ProductViewSet
from customers.views import CustomerViewSet
from orders.views import OrderViewSet
from supplier_order.views import SupplierOrderViewSet
from suppliers.views import SupplierViewSet, PurchaseOrderViewSet
from invoices.views import InvoiceViewSet
from payments.views import PaymentViewSet
from account.views import ShopAccountView
from load_calculator.views import LoadCalculationViewSet
from quotations.views import QuotationViewSet
from reports.views import (
    SalesReportView, InventoryReportView, CustomerReportView,
    FinancialReportView, SupplierReportView, ReportsViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'purchase-orders', PurchaseOrderViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'load-calculations', LoadCalculationViewSet)
router.register('supplier-orders', SupplierOrderViewSet, basename='supplier-orders')
router.register(r'quotations', QuotationViewSet)
    
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/quotations/', include('quotations.urls')),
    path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include(([
        path('register/', AuthViewSet.as_view({'post': 'register'})),
        path('profile/', AuthViewSet.as_view({'get': 'profile'})),
        path('update_profile/', AuthViewSet.as_view({'put': 'update_profile'})),
    ]))),
    path('api/reports/sales/', SalesReportView.as_view(), name='sales-report'),
    path('api/reports/inventory/', InventoryReportView.as_view(), name='inventory-report'),
    path('api/reports/customers/', CustomerReportView.as_view(), name='customer-report'),
    path('api/reports/financial/', FinancialReportView.as_view(), name='financial-report'),
    path('api/reports/suppliers/', SupplierReportView.as_view(), name='supplier-report'),
    # path('api/reports/supplier-payments/', SupplierOrderViewSet.as_view(), name='supplier-payments'),
    path('api/account/shop-account/', ShopAccountView.as_view(), name='shop-account'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)