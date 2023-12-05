from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    
    def __str__(self):
        return f"{self.username}, {self.first_name}, {self.last_name}, {self.email}"
    
class Transfer(models.Model):
    transfer_date = models.DateField()
    transfer_sum = models.IntegerField()
    transfer_currency = models.CharField(max_length=5)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transfers")
    
    def __str__(self):
        return f"On day {self.transfer_date} user {self.owner} transfered {self.transfer_sum} {self.transfer_currency}"
    
class Forex(models.Model):
    forex_date = models.DateField()
    selling_sum = models.FloatField()
    selling_currency = models.CharField(max_length=5)
    rate = models.FloatField()
    purchasing_sum = models.FloatField()
    purchasing_currency = models.CharField(max_length=5)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="forexes")
    
    def __str__(self):
        return f"On day {self.forex_date} user {self.owner} purchased {self.purchasing_sum} {self.purchasing_currency} for {self.selling_sum} {self.selling_currency} ({self.rate})"
    
