from django import forms

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
    transfer_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control mb-3'}), label='Date of transfer')
    transfer_sum = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}), label='Sum of transfer')
    transfer_currency = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Currency of transfer')
    
class ForexForm(forms.Form):
    forex_date = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'Date of forex', 'type': 'date', 'class': 'form-control mb-3'}), label='')
    rate = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder': 'Rate', 'id': 'rate', 'class' : 'form-control mb-3'}), label='')
    selling_currency = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Selling currency', 'id': 'sell-curr', 'class': 'form-control mb-3'}), label='')
    selling_sum = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder': 'Selling sum', 'id': 'sell-sum', 'class': 'form-control mb-3'}), label='')
    purchasing_currency = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Purchasing currency', 'id': 'buy-curr', 'class': 'form-control mb-auto'}), label='')
    
    