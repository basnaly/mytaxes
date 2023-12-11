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
    
    def get_year(self):
        return self.transfer_date.year
    
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
  
class Buy_Stock(models.Model):
    buy_date = models.DateField()
    stock = models.CharField(max_length=10)
    price = models.FloatField()
    quantity = models.IntegerField()
    sum_of_stocks = models.FloatField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stocks")
    
    def __str__(self):
        return f"{self.buy_date} {self.stock} {self.price} {self.quantity} {self.sum_of_stocks} {self.owner}"
      
class Dividend_Tax(models.Model):
    dividend_date = models.DateField()
    stock = models.CharField(max_length=10)
    dividend_per_share = models.FloatField()
    quantity = models.IntegerField()
    dividend_sum = models.FloatField()
    tax = models.FloatField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dividents") 
    
    def __str__(self):
        return f"{self.dividend_date} {self.stock} {self.dividend_per_share} {self.quantity} {self.dividend_sum} {self.tax} {self.owner}"