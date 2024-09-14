from django.forms.models import ModelForm
from django import forms
from .models import Item


class UpdateItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ["name", "description", "price_in_cents"]
        widgets = {
            "name": forms.TextInput(),
            "description": forms.Textarea(),
            "price_in_cents": forms.NumberInput(),
        }
