"""Админ-зона."""
from django.contrib import admin

from .models import ProfileUser, Subscriptions

admin.site.register(Subscriptions)
admin.site.register(ProfileUser)
