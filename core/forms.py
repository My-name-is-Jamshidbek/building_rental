# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from core.models import Client, Product, ProductMold, Trash



class CustomUserCreationForm(UserCreationForm):
    # This creation form already includes password1 and password2.
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

class UserUpdateForm(forms.ModelForm):
    # Optional password field. If left blank, the password remains unchanged.
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        help_text="Leave blank if you don't want to change the password."
    )
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password")

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['fullname', 'phone', 'desc']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'count']


class ProductMoldForm(forms.ModelForm):
    class Meta:
        model = ProductMold
        fields = ['length', 'price', 'count']


class TrashForm(forms.ModelForm):
    class Meta:
        model = Trash
        # Expose only client and prepayment on creation.
        fields = ['client', 'prepayment']