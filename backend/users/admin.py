"""Админ-зона."""
from django.contrib import admin

from .models import Subscriptions, UserEmail

admin.site.register(Subscriptions)
admin.site.register(UserEmail)
