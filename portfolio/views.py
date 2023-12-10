from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.http import HttpResponseRedirect, JsonResponse
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.db.models import Sum
from portfolio.forms import RegisterForm, LoginForm, TransferForm, ForexForm, Buy_StockForm, Dividend_TaxForm
from django.contrib import messages

import datetime
from .models import User, Transfer, Forex, Buy_Stock, Dividend_Tax


COMMITIONS = {
    "Forex": 2,
    "Buy": 1
}


def index(request):
    user = User.objects.get(id=request.user.id)
    return render(request, "portfolio/index.html", {
        "user": user,
    })
    
def register(request):
    if request.method == "GET":
        return render(request, "portfolio/register.html", {
            "form": RegisterForm
        })   
    else:
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            password = form.cleaned_data["password"]
            confirmation = form.cleaned_data["confirmation"]
            
            if password != confirmation:
                return render(request, "petclinic/register.html", {
                    "message": "Password must match conformation."
                })
            try:
                new_user = User.objects.create_user(
                    username = username,
                    email = email,
                    first_name = first_name,
                    last_name =last_name,
                    password = password,
                )
                new_user.save()
            except IntegrityError:
                return render(request, "portfolio/register.html", {
                    "message": "User already taken!",
                    "form": form
                })
            login(request, new_user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request,"portfolio/register.html", {
                    "message": "Some of the values are not valid!",
                    "form": form
                })
        
    
def login_view(request):
    if request.method == "GET":
        return render(request, "portfolio/login.html", {
            "form": LoginForm
        })
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "portfolio/login.html", {
                    "message": "Invalid username or password!",
                    "form": form
                })
        else:
            return render(request, "portfolio/login.html", {
                "message": "The form is not valid!",
                "form": form
            })
        

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
   
   
def get_previous_year(request): 
    previous_year = datetime.datetime.now().year - 1
    return JsonResponse({
        "previous_year": str(previous_year)
    })


@login_required   
def transfer(request):
    user = User.objects.get(id=request.user.id)
    user_transfers = Transfer.objects.filter(owner=user)
    # abc = sum([el.transfer_sum for el in user_transfers])
    transfers_sum = Transfer.objects.all().aggregate(Sum('transfer_sum'))['transfer_sum__sum']
    
    if request.method == "GET":
        return render(request, "portfolio/transfer.html", {
            "form": TransferForm,
            "transfers": user_transfers,
            "transfers_sum": transfers_sum,
        })
    else:
        form = TransferForm(request.POST)
        if form.is_valid():
            transfer_date = form.cleaned_data["transfer_date"]
            transfer_sum = form.cleaned_data["transfer_sum"]
            transfer_currency = form.cleaned_data["transfer_currency"]
            try:
                new_transfer = Transfer.objects.create(
                    transfer_date = transfer_date,
                    transfer_sum = transfer_sum,
                    transfer_currency = transfer_currency,
                    owner = user
                )
                new_transfer.save()
            except IntegrityError:
                messages.error(request, "Something went wrong. Try again later.")
                return render(request, "portfolio/transfer.html", {
                    "form": form,
                    "transfers": user_transfers,
                    "transfers_sum": transfers_sum,
                })
            messages.success(request, f"Your transfer of { transfer_sum } {transfer_currency} was successfully saved!")
            return HttpResponseRedirect(reverse("transfer"))
        else:
            messages.error(request, "The form is not valid!")
            return render(request, "portfolio/transfer.html", {
                "form": form,
                "transfers": user_transfers,
                "transfers_sum": transfers_sum,
            })
            

@login_required
def forex(request):
    user = User.objects.get(id=request.user.id)   
    user_exchanges = Forex.objects.filter(owner=user)
    selling_sums = round(Forex.objects.all().aggregate(Sum('selling_sum'))['selling_sum__sum'], 2)
    purchasing_sums = round(Forex.objects.all().aggregate(Sum('purchasing_sum'))['purchasing_sum__sum'], 2)

    if request.method == "GET":
        return render(request, "portfolio/forex.html", {
            "form": ForexForm,
            "exchanges": user_exchanges,
            "selling_sums": selling_sums,
            "purchasing_sums": round(purchasing_sums, 2),
        })  
    else:
        form = ForexForm(request.POST)
        if form.is_valid():
            forex_date = form.cleaned_data["forex_date"]
            selling_sum = form.cleaned_data["selling_sum"]
            selling_currency = form.cleaned_data["selling_currency"]
            rate = form.cleaned_data["rate"] 
            purchasing_currency = form.cleaned_data["purchasing_currency"]
            try:
                new_forex = Forex.objects.create(
                    forex_date = forex_date, 
                    selling_sum = selling_sum,
                    selling_currency = selling_currency,
                    rate = rate,
                    purchasing_sum = round(selling_sum/rate, 2),
                    purchasing_currency = purchasing_currency,
                    owner = user
                )
                new_forex.save()
            except IntegrityError:
                messages.error(request, "Something went wrong. Try again later.")
                return render(request, "portfolio/forex.html", {
                    "form": form,
                    "exchanges": user_exchanges,
                    "selling_sums": selling_sums,
                    "purchasing_sums": round(purchasing_sums, 2),
                })
            messages.success(request, f"Your request to exchange { selling_currency } { selling_sum } to { purchasing_currency } was successfully done!")
            return HttpResponseRedirect(reverse("forex"))
        else:
            messages.error(request, "The form is not valid!")
            return render(request, "portfolio/forex.html", {
                "form": form,
                "exchanges": user_exchanges,
                "selling_sums": selling_sums,
                "purchasing_sums": purchasing_sums,
            })
            
            
@login_required
def buy_stock(request):
    user = User.objects.get(id=request.user.id)
    stocks = Buy_Stock.objects.filter(owner=user)
    total_stocks_sum = sum([el.sum_of_stocks for el in stocks])
    
    if request.method == "GET":
        return render(request, "portfolio/buy_stock.html", {
            "form": Buy_StockForm(),
            "stocks": stocks,
            "total_stocks_sum": total_stocks_sum,
        })
        
    else:
        form = Buy_StockForm(request.POST)
        if form.is_valid():
            buy_date = form.cleaned_data["buy_date"]
            stock = form.cleaned_data["stock"]
            price = form.cleaned_data["price"]
            quantity = form.cleaned_data["quantity"]
            try:
                purchased_stocks = Buy_Stock.objects.create(
                    buy_date = buy_date,
                    stock = stock,
                    price = price,
                    quantity = quantity,
                    sum_of_stocks = round(price * quantity, 2),
                    owner = user
                ) 
                purchased_stocks.save()
            except IntegrityError:
                messages.error(request, "Something went wrong. Try again later.")
                return render(request, "portfolio/buy_stock.html", {
                    "form": form,
                    "stocks": stocks,
                    "total_stocks_sum": total_stocks_sum,
                })
            messages.success(request, f"Your request to buy { quantity } { stock } stocks was successfully saved!")
            return HttpResponseRedirect(reverse("buy_stock"))
        else:
            messages.error(request, "The form is not valid!")
            return render(request, "portfolio/buy_stock.html", {
                "form": form,
                "stocks": stocks,
                "total_stocks_sum": total_stocks_sum,
            })
            
            
@login_required
def dividend_tax(request):
    user = User.objects.get(id=request.user.id)
    dividends_taxes = Dividend_Tax.objects.filter(owner=user)
    stocks = Buy_Stock.objects.filter(owner=user).values('stock').distinct()
    stock_options = [(el['stock'], el['stock']) for el in stocks]
    total_dividends = round(sum([el.dividend_sum for el in dividends_taxes]), 2)
    total_taxes = round(sum([el.tax for el in dividends_taxes]), 2)
    
    if request.method == "GET":
        form = Dividend_TaxForm()
        form.fields['stock'].widget.choices = stock_options
        return render(request, "portfolio/dividend_tax.html", {
            "form": form,
            "dividends_taxes": dividends_taxes,
            "total_dividends": total_dividends,
            "total_taxes": total_taxes
        })
        
    else:
        form = Dividend_TaxForm(request.POST)
        if form.is_valid():
            dividend_date = form.cleaned_data["dividend_date"]
            stock = form.cleaned_data["stock"]
            dividend_per_share = form.cleaned_data["dividend_per_share"]
            quantity = form.cleaned_data["quantity"]
            try:
                dividend_tax = Dividend_Tax.objects.create(
                    dividend_date = dividend_date,
                    stock = stock,
                    dividend_per_share = dividend_per_share,
                    quantity = quantity,
                    dividend_sum = round(dividend_per_share * quantity, 2),
                    tax = round(dividend_per_share * 0.25 * quantity, 2),
                    owner = user
                )
                dividend_tax.save()
            except: 
                messages.error(request, "Something went wrong. Try again later.")
                return render(request, "portfolio/dividend_tax.html", {
                    "form": form,
                    "dividends_taxes": dividends_taxes,
                    "total_dividends": total_dividends,
                    "total_taxes": total_taxes,
                })
            messages.success(request, f"You dividend of {dividend_per_share} for {stock} stock was saccessfully added!")
            return HttpResponseRedirect("dividend_tax")
        else:
            messages.error(request, "The form is not valid!")
            return render(request, "portfolio/dividend_tax.html", {
                "form": form,
                "dividends_taxes": dividends_taxes,
                "total_dividends": total_dividends,
                "total_taxes": total_taxes
            })