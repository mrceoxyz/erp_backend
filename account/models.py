from django.db import models

class ShopAccount(models.Model):
    name = models.CharField(max_length=100, default='Main Account')
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=1000000000)

    def __str__(self):
        return f"{self.name} - {self.balance}"
