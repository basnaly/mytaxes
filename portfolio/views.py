from math import ceil
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.http import HttpResponseRedirect, JsonResponse
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.db.models import Sum
from config import API_KEY
from portfolio.forms import RegisterForm, LoginForm, TransferForm, ForexForm, Buy_StockForm, Dividend_TaxForm, Sell_StockForm, ProfileForm
from django.contrib import messages
import requests
from django.contrib.auth import update_session_auth_hash
import datetime
from .models import User, Transfer, Forex, Buy_Stock, Dividend_Tax, Sell_Stocks
from django.contrib.auth.hashers import check_password


COMMITIONS = {
    "Forex": 2,
    "Buy": 1
}


def index(request):
    user = User.objects.get(id=request.user.id)
    
    # dropdown
    first_transfer = Transfer.objects.filter(owner=user).order_by("transfer_date")[0]
    start_year = first_transfer.get_year()
    end_year = datetime.datetime.today().year + 1
    list_years = []
    for i in range(start_year, end_year):
        list_years.append(str(i))
       
    # calculate starting cash for previows and current years
    selected_year = request.GET.get('year')
    if selected_year: 
        # calculate forex sum for previows year
        old_forex_list = Forex.objects.filter(
            owner=user, 
            forex_date__lte=datetime.datetime(year=int(selected_year), month=1, day=1, hour=0, minute=0)
        )
        old_forex_sum = round(sum([el.purchasing_sum for el in old_forex_list]), 2)

        # calculate sum_of_stocks for previows year
        old_stocks_list = Buy_Stock.objects.filter(
            owner=user,
            buy_date__lte=datetime.datetime(year=int(selected_year), month=1, day=1, hour=0, minute=0)
        )
        old_stocks_sum = round(sum(el.sum_of_stocks for el in old_stocks_list), 2)
        
        # calculate dividend_sum and taxes for previows year
        old_dividends_list = Dividend_Tax.objects.filter(
            owner=user,
            dividend_date__lte=datetime.datetime(year=int(selected_year), month=1, day=1, hour=0, minute=0)
        )
        old_dividends_sum = round(sum(el.dividend_sum for el in old_dividends_list), 2)
        old_taxes_sum = round(sum(el.tax for el in old_dividends_list), 2)
        
        # clculate commisions for previows year
        old_commitions = len(old_forex_list) * COMMITIONS["Forex"] + len(old_stocks_list) * COMMITIONS["Buy"]
        
        # calculate starting cash for previows year
        starting_cash = round(old_forex_sum + old_dividends_sum - old_stocks_sum - old_taxes_sum - old_commitions, 2)
        
        
        # calculate transfer_sum for current year
        current_transfer_list = Transfer.objects.filter(
            owner=user,
            transfer_date__gte=datetime.datetime(year=int(selected_year), month=1, day=1, hour=0, minute=0)
        )
        current_transfer_sum = round(sum([el.transfer_sum for el in current_transfer_list]), 2)
        
        # calculate forex sum for current year
        current_forex_list = Forex.objects.filter(
            owner=user, 
            forex_date__gte=datetime.datetime(year=int(selected_year), month=1, day=1, hour=0, minute=0)
        )
        current_forex_sum = round(sum([el.purchasing_sum for el in current_forex_list]), 2)

        # calculate sum_of_stocks for current year
        current_stocks_list = Buy_Stock.objects.filter(
            owner=user,
            buy_date__gte=datetime.datetime(year=int(selected_year), month=1, day=1, hour=0, minute=0)
        ).order_by("-buy_date")
        current_stocks_sum = round(sum(el.sum_of_stocks for el in current_stocks_list), 2)
        
        # calculate dividend_sum and taxes for current year
        current_dividends_list = Dividend_Tax.objects.filter(
            owner=user,
            dividend_date__gte=datetime.datetime(year=int(selected_year), month=1, day=1, hour=0, minute=0)
        )
        current_dividends_sum = round(sum(el.dividend_sum for el in current_dividends_list), 2)
        current_taxes_sum = round(sum(el.tax for el in current_dividends_list), 2)
        
        # clculate commisions for current year
        current_commitions = len(current_forex_list) * COMMITIONS["Forex"] + len(current_stocks_list) * COMMITIONS["Buy"]
        
        # calculate starting cash for previows year
        ending_cash = round(current_forex_sum + current_dividends_sum - current_stocks_sum - current_taxes_sum - current_commitions, 2)
        
        
        ending_sum = 0
        
        date_to_use = check_date(int(selected_year))
        formatted_date = date_to_use.strftime("%Y-%m-%d")

        for stock in current_stocks_list:
            endpoint = f'https://api.polygon.io/v1/open-close/{stock.stock}/{formatted_date}?adjusted=true&apiKey={API_KEY}'
            
            response = requests.get(endpoint)
            data = response.json()

            # Extract the ending_price
            try:
                ending_price = data['close']
                stock.set_ending_price(ending_price) # stock.set_ending_price(50.68)
                ending_sum += stock.ending_sum

            except KeyError:
                print(f'Unable to retrieve data for {stock.stock}')
                      
        lost = round(current_stocks_sum - ending_sum, 2)
        earn = round(ending_sum - current_stocks_sum, 2)
        
        return render(request, "portfolio/index.html", {
            "list_years": list_years,
            "selected_year": selected_year,
            "starting_cash": starting_cash,
            "current_transfer_sum": current_transfer_sum,
            "current_forex_sum": current_forex_sum,
            "current_stocks_sum": current_stocks_sum,
            "current_dividends_sum": current_dividends_sum,
            "current_taxes_sum": current_taxes_sum,
            "current_commitions": current_commitions,
            "ending_cash": ending_cash,
            "current_stocks_list": current_stocks_list,
            "ending_sum": ending_sum,
            "lost": lost,
            "earn": earn
        })
    
    return render(request, "portfolio/index.html", {
        "list_years": list_years,
        "selected_year": selected_year,
    })
    

def check_date(selected_year):
    today = datetime.datetime.now()
    if today.year == selected_year:
        return today - datetime.timedelta(days=1)
    else:
        end_of_selected_year = datetime.datetime(selected_year, 12, 31)
        return end_of_selected_year
    
  
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
                return render(request, "portfolio/register.html", {
                    "message": "Password must match conformation."
                })
            try:
                new_user = User.objects.create_user(
                    username = username,
                    email = email,
                    first_name = first_name,
                    last_name = last_name,
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
    return HttpResponseRedirect(reverse("login"))
   

@login_required
def profile(request):
    user = User.objects.get(id=request.user.id)
    if request.method == "GET":
        return render(request, "portfolio/profile.html", {
            "form": ProfileForm(initial={
                "email": user.email,
                "first_name": user.first_name,
                "last_name":user.last_name
            })
        })
       
    else:
        form = ProfileForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            current_password = form.cleaned_data.get("current_password")
            new_password = form.cleaned_data.get("new_password")
            confirmation = form.cleaned_data.get("confirmation")
            
            if not check_password(current_password, user.password):
                messages.error(request, "The current password does't match.")
                return render(request, "portfolio/profile.html", {
                    "form": form
                })
            
            if new_password:
                if new_password != confirmation:
                    messages.error(request, "The new password must match conformation.")
                    return render(request, "portfolio/profile.html", {
                        "form": form
                    })
                else:
                    user.set_password(new_password)
                
            try:
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                update_session_auth_hash(request, user)
                
            except IntegrityError:
                messages.error(request, "Something went wrong. Try again later.")
                return render(request, "portfolio/profile.html", {
                    "form": form
                })
            messages.success(request, "Your profile was successfully changed!")
            return HttpResponseRedirect(reverse("index"))
        
        else: 
            messages.error(request, "The form is not valid!")
            return redirect(request, "portfolio/profile.html", {
                "form": form
            })     


@login_required   
def transfer(request):
    user = User.objects.get(id=request.user.id)
    user_transfers = Transfer.objects.filter(owner=user).order_by("-transfer_date")
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
    user_exchanges = Forex.objects.filter(owner=user).order_by("-forex_date")
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
    stocks = Buy_Stock.objects.filter(owner=user).order_by("-buy_date")
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
    dividends_taxes = Dividend_Tax.objects.filter(owner=user).order_by("-dividend_date")
    stocks = Buy_Stock.objects.filter(owner=user).values('stock').distinct()
    stock_options = [(el['stock'], el['stock']) for el in stocks]
    total_dividends = sum([el.dividend_sum for el in dividends_taxes])
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
                    tax = round(ceil(dividend_per_share * 2500) / 10000  * quantity * 100) / 100,
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
 
@login_required 
def get_stock_quantity(request):
    user = User.objects.get(id=request.user.id)
    
    # request.GET = {"stock_symbol":"VTI"}  request.GET["stock_symbol"] => "VTI"  request.GET.get("stock_symbol") => "VTI"
    # url 127.../get_stock_quantity?stock_symbol=VTI
    
    user_bought_stocks = Buy_Stock.objects.filter(owner=user, stock=request.GET.get('stock_symbol'))
    # If form selested FLOT
    # <QuerySet [<Buy_Stock: 2023-08-24 FLOT 50.795 100 5079.5 basnaly, nataly, bas, basnaly@gmail.com>, 
    #            <Buy_Stock: 2023-11-02 FLOT 50.6193 20 1012.39 basnaly, nataly, bas, basnaly@gmail.com>]>
    total_bought_stocks = sum([el.quantity for el in user_bought_stocks])
    average_buy_price = round(sum([el.sum_of_stocks for el in user_bought_stocks]) / total_bought_stocks, 2)
    
    user_sold_stocks = Sell_Stocks.objects.filter(owner=user, stock=request.GET.get('stock_symbol'))
    total_sold_stocks = sum(el.quantity for el in user_sold_stocks)
    
    total_stocks = total_bought_stocks - total_sold_stocks
    
    return JsonResponse({
        "total_stocks": total_stocks,
        "average_buy_price": average_buy_price
    })


@login_required
def sell_stock(request):
    user = User.objects.get(id=request.user.id)       
    stocks = Buy_Stock.objects.filter(owner=user).values("stock").distinct()
    # [{'stock': 'VTI'}, {'stock': 'HDV'}, {'stock': 'FLOT'}]

    stock_options = [(el['stock'], el['stock']) for el in stocks]
    # [('VTI', 'VTI'), ('HDV', 'HDV'), ('FLOT', 'FLOT')]
    
    form = Sell_StockForm()
    form.fields['stock'].widget.choices = [('', 'Select symbol')] + stock_options
    
    sold_stocks = Sell_Stocks.objects.filter(owner=user).order_by("-sell_date")
     
    if request.method == "GET":
        return render(request, "portfolio/sell_stock.html",{
            "form": form,
            "sold_stocks": sold_stocks
        })
        
    else:
        form = Sell_StockForm(request.POST)
        if form.is_valid():
            sell_date = form.cleaned_data["sell_date"]
            stock = form.cleaned_data["stock"]
            price = form.cleaned_data["price"]
            quantity = form.cleaned_data["quantity"]
            
            user_bought_stocks = Buy_Stock.objects.filter(owner=user, stock=stock)
            total_bought_stocks = sum([el.quantity for el in user_bought_stocks])
            user_sold_stocks = Sell_Stocks.objects.filter(owner=user, stock=stock)
            total_sold_stocks = sum([el.quantity for el in user_sold_stocks])
            total_stocks = total_bought_stocks - total_sold_stocks
            
            if not total_stocks:
                average_buy_price = 0
            else:
                average_buy_price = round(sum([el.sum_of_stocks for el in user_bought_stocks]) / total_bought_stocks, 2)
            if total_stocks >= quantity:
                try:
                    sum_of_stocks = round(price * quantity, 2)
                    tax = round((sum_of_stocks - (average_buy_price * quantity)) * 25 / 100, 2)
                    print(tax)
                    sold_stock = Sell_Stocks.objects.create(
                        sell_date = sell_date,
                        stock = stock,
                        price = price, 
                        quantity = quantity,
                        sum_of_stocks = sum_of_stocks,
                        tax = tax,
                        owner = user
                    )
                    sold_stock.save()
                except Exception as e:
                    print(e)
                    messages.error(request, "Something went wrong. Try again later.")
                    return render(request, "portfolio/sell_stock.html", {
                        "form": form,
                        "sold_stocks": sold_stocks
                    })
                messages.success(request, f"You sell of {quantity} {stock} stocks was successfully added!")
                return HttpResponseRedirect("sell_stock")
            else:
                messages.error(request, f"You have only {total_stocks} {stock} stocks!")
                return HttpResponseRedirect("sell_stock")
                
        else:
            messages.error(request, "The form is not valid!")
            return HttpResponseRedirect("sell_stock")
                