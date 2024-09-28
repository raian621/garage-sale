"""Forms used by the shop application."""

from django import forms
from django.forms.models import ModelForm

from .models import Item, Order


class UpdateItemForm(ModelForm):
    """Form used to update an Item."""

    class Meta:
        """Metadata class."""

        model = Item
        fields = ["name", "description", "price_in_cents"]
        widgets = {
            "name": forms.TextInput(),
            "description": forms.Textarea(),
            "price_in_cents": forms.NumberInput(),
        }


class CheckoutForm(ModelForm):
    """Form used to check out a customer."""

    class Meta:
        """Metadata class."""

        model = Order
        fields = ["first_name", "last_name", "email"]
