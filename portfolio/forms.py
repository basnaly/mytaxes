from django import forms
from .models import User, Transfer, Forex, Buy_Stock
from datetime import date



class RegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}), label='')
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}), label='')
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}), label='')
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}), label='')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}), label='')
    confirmation = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirmation', 'class': 'form-control'}), label='')

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control mb-3'}), label='')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}), label='')
    
class TransferForm(forms.Form):
    transfer_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control mb-3', 'max': str(date.today())}), label='Date of transfer')
    transfer_sum = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}), label='Sum of transfer')
    transfer_currency = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Currency of transfer')
    
class ForexForm(forms.Form):
    forex_date = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'Date of forex', 'type': 'date', 'class': 'form-control mb-3', 'max': str(date.today())}), label='')
    selling_currency = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Selling currency', 'id': 'sell-curr', 'class': 'form-control mb-3'}), label='')
    selling_sum = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder': 'Selling sum', 'id': 'sell-sum', 'class': 'form-control mb-3'}), label='')
    rate = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder': 'Rate', 'id': 'rate', 'class' : 'form-control mb-3'}), label='')
    purchasing_currency = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Purchasing currency', 'id': 'buy-curr', 'class': 'form-control mb-3'}), label='')
    
class Buy_StockForm(forms.Form):
    buy_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control mb-3', 'max': str(date.today())}), label='')
    stock = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Symbol of stock', 'class': 'form-control mb-3'}), label='')
    price = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder': 'Price of stock', 'id': 'price-stock', 'class': 'form-control mb-3'}), label='')
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Q-ty of stocks', 'id': 'quantity-stocks', 'class': 'form-control mb-3'}), label='')
       
class Dividend_TaxForm(forms.Form):
    dividend_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control mb-3', 'max': str(date.today())}), label='')
    stock = forms.CharField(widget=forms.Select(attrs={'plaseholder': 'Symbol of stock', 'class': 'form-control mb-3'}, choices=[]),  label='')
    dividend_per_share = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder': 'Dividend per share', 'id': 'dividend-share', 'class': 'form-control mb-3'}), label='')
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Q-ty of stocks', 'id': 'quantity-stocks', 'class': 'form-control mb-3'}), label='')
    