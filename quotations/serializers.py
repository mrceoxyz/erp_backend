from rest_framework import serializers
from .models import Quotation

class QuotationSerializer(serializers.ModelSerializer):
    inverter = serializers.StringRelatedField()
    battery = serializers.StringRelatedField()
    solar_panel = serializers.StringRelatedField()

    class Meta:
        model = Quotation
        fields = '__all__'
