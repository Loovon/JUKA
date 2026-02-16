# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from sellers.forms import SellerProfileForm


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)
    phone_number = forms.CharField(label="Phone Number")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'role', 'password1', 'password2')

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.seller_form = SellerProfileForm()

        def is_seller_selected(self):
            return self.cleaned_data.get('role') == 'seller'


class CustomAuthenticationForm(AuthenticationForm):
    pass
