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
from portfolio.forms import RegisterForm, LoginForm, TransferForm, ForexForm

import datetime
from .models import User, Transfer, Forex


def index(request):
    user = User.objects.get(id=request.user.id)
    previous_year = datetime.datetime.now().year - 1
    return render(request, "portfolio/index.html", {
        "user": user,
        "previous_year": previous_year
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
   

@login_required   
def transfer(request):
    user = User.objects.get(id=request.user.id)
    user_transfers = Transfer.objects.filter(owner=user)
    
    if request.method == "GET":
        return render(request, "portfolio/transfer.html", {
            "form": TransferForm,
            "transfers": user_transfers
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
                return render(request, "portfolio/transfer.html", {
                    "message": "Something went wrong. Try again later.",
                    "form": form,
                    "transfers": user_transfers
                })
            return render(request, "portfolio/index.html", {
                "message": f"Your transfer of { transfer_sum } {transfer_currency} was successfully saved!",
                "transfer_sum": transfer_sum,
                "transfer_currency": transfer_currency,
                "transfers": user_transfers
            })
        else:
            return render(request, "portfolio/transfer.html", {
                "message": "The form is not valid!",
                "form": form,
                "transfers": user_transfers
            })
            

@login_required
def forex(request):
    user = User.objects.get(id=request.user.id)    
    if request.method == "GET":
        return render(request, "portfolio/forex.html", {
            "form": ForexForm
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
                return render(request, "portfolio/forex.html", {
                    "message": "Something went wrong. Try again later.",
                    "form": form
                })
            return render(request, "portfolio/index.html", {
                "message": f"Your request to exchange { selling_currency } { selling_sum } to { purchasing_currency } was successfully done!",
                "form": form
            })
        else:
            return render(request, "portfolio/forex.html", {
                "message": "The form is not valid!",
                "form": form
            })
            
            
         