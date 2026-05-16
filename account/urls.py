# accounts/urls.py
from django.urls import path
from .views import ShopAccountView

urlpatterns = [
    path('shop-account/', ShopAccountView.as_view(), name='shop-account'),
]
