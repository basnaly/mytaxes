from django.contrib import admin

from .models import User, Transfer

# Register your models here.

admin.site.register(User)
admin.site.register(Transfer)
