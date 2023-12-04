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
        return f"{self.transfer_date} {self.transfer_sum} {self.owner}"