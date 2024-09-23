"""Админ-зона."""
from django.contrib import admin

from .models import CustomUser, Subscriptions

admin.site.register(Subscriptions)
admin.site.register(CustomUser)
