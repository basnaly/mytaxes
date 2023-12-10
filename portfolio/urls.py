from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    
    path("get_previous_year", views.get_previous_year, name="get_previous_year"),
    
    path("transfer", views.transfer, name="transfer"),
    path("forex", views.forex, name="forex"),
    path("buy_stock", views.buy_stock, name="buy_stock"),
    
    path("dividend_tax", views.dividend_tax, name="dividend_tax"),
    
]