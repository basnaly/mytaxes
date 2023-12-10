from django.contrib import admin

from .models import User, Transfer, Forex, Buy_Stock, Dividend_Tax

# Register your models here.

admin.site.register(User)
admin.site.register(Transfer)
admin.site.register(Forex)
admin.site.register(Buy_Stock)
admin.site.register(Dividend_Tax)