from django import forms
from .models import SellerProfile
from .models import ShopImage
from .models import Shop


class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['store_name', 'store_description', 'address', 'phone_number']


from .models import Advert


class AdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = [
            "title",
            "description",
            "category",
            "price",
            "type",
            "size",
            "thickness",
            "color",
            "weight",
            "shape",
            "image",
            "attributes",
            "active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "attributes": forms.Textarea(attrs={"rows": 2}),
        }

        def save(self, commit=True):
            advert = super().save(commit=False)
            advert.seller = self.initial['seller']
            advert.shop = self.initial['shop']
            if commit:
                advert.save()
            return advert


class ShopImageForm(forms.ModelForm):
    class Meta:
        model = ShopImage
        fields = ["image"]

    image = forms.ImageField(required=True)



class ShopSettingsForm(forms.ModelForm):
        class Meta:
            model = Shop
            fields = [
                "shop_name", "description", "location",
                "logo", "banner",
                "email", "phone", "address", "delivery_areas",
                "payment_number", "bank_account",
                "refund_policy", "delivery_policy",
                "active", "notify_on_order", "rank",
            ]
            labels = {
                "shop_name": "Shop Name",
                "description": "About Your Shop",
                "location": "Shop Location",
                "logo": "Shop Logo",
                "banner": "Shop Banner",
                "payment_number": "M-Pesa Number",
                "bank_account": "Bank Account",
                "refund_policy": "Refund Policy",
                "delivery_policy": "Delivery Policy",
                "active": "Active Shop",
                "notify_on_order": "Notify me on new orders",
                "rank": "Membership Rank",
            }
            widgets = {
                "description": forms.Textarea(attrs={"rows": 3}),
                "delivery_areas": forms.Textarea(attrs={"rows": 2}),
                "refund_policy": forms.Textarea(attrs={"rows": 2}),
                "delivery_policy": forms.Textarea(attrs={"rows": 2}),
            }



