from rest_framework.routers import DefaultRouter
from .views import QuotationViewSet

router = DefaultRouter()
router.register('', QuotationViewSet)

urlpatterns = router.urls
