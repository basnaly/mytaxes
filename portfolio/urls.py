from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    
    path("transfer", views.transfer, name="transfer"),
    path("forex", views.forex, name="forex"),
    path("buy_stock", views.buy_stock, name="buy_stock"),
    
    path("dividend_tax", views.dividend_tax, name="dividend_tax"),
    path("sell_stock", views.sell_stock, name="sell_stock"),
    path("get_stock_quantity", views.get_stock_quantity, name="get_stock_quantity"),
    
]