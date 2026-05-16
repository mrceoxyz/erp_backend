# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ShopAccount
from .serializers import ShopAccountSerializer

class ShopAccountView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        account = ShopAccount.objects.first()
        serializer = ShopAccountSerializer(account)
        return Response(serializer.data)
