# accounts/serializers.py
from rest_framework import serializers
from .models import ShopAccount

class ShopAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopAccount
        fields = ['id', 'name', 'balance']
