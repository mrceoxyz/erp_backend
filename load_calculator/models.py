from django.db import models
from customers.models import Customer

class LoadCalculation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='load_calculations')
    name = models.CharField(max_length=200)
    total_watts = models.DecimalField(max_digits=10, decimal_places=2)
    total_watt_hours = models.DecimalField(max_digits=10, decimal_places=2)
    recommended_inverter = models.CharField(max_length=50)
    recommended_battery_count = models.IntegerField()
    recommended_solar_panels = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.customer.name}"

class LoadAppliance(models.Model):
    calculation = models.ForeignKey(LoadCalculation, on_delete=models.CASCADE, related_name='appliances')
    name = models.CharField(max_length=100)
    watts = models.IntegerField()
    quantity = models.IntegerField(default=1)
    hours_per_day = models.DecimalField(max_digits=4, decimal_places=2)
    
    @property
    def daily_consumption(self):
        return self.watts * self.quantity * float(self.hours_per_day)
    
    def __str__(self):
        return f"{self.name} - {self.watts}W"