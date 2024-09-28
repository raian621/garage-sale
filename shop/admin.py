"""Admin settings for the shop application."""

from django.contrib import admin

from .models import Item

admin.site.register(Item)
