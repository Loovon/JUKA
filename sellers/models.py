# sellers/models.py
from django.db import models
from django.conf import settings


class SellerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=100)
    store_description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Seller: {self.store_name}"


class Shop(models.Model):
    seller = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shop'
    )
    shop_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    # optional later for Google Maps
    location = models.CharField(max_length=255, blank=True, null=True)  # e.g., "Nairobi, Kenya"
    # Media
    logo = models.ImageField(upload_to="shops/logos/", blank=True, null=True)
    banner = models.ImageField(upload_to="shops/banners/", blank=True, null=True)
    # Contact & Location
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    delivery_areas = models.TextField(blank=True, null=True, help_text="List of areas served (comma separated)")
    # Payment
    payment_number = models.CharField(max_length=50, blank=True, null=True, help_text="Mpesa / Mobile Money")
    bank_account = models.CharField(max_length=100, blank=True, null=True)

    # Policies
    refund_policy = models.TextField(blank=True, null=True)
    delivery_policy = models.TextField(blank=True, null=True)

    # Preferences
    active = models.BooleanField(default=True)
    notify_on_order = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    rank = models.CharField(
        max_length=20,
        choices=[("hustler", "Hustler"), ("verified", "Verified"), ("pro", "Pro")],
        default="hustler"
    )

    def __str__(self):
        return self.shop_name


class Advert(models.Model):
    shop = models.ForeignKey(
        Shop,
        related_name='adverts',
        on_delete=models.CASCADE
    )
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey("categories.Category", related_name="adverts", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    thickness = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    weight = models.CharField(max_length=50, blank=True, null=True)  # <-- new
    shape = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to="adverts/")
    created_at = models.DateTimeField(auto_now_add=True)
    # new fields
    attributes = models.TextField(blank=True, null=True)  # freeform attributes
    active = models.BooleanField(default=True)  # Active or Draft

class AdvertVariant(models.Model):
    advert = models.ForeignKey(Advert, related_name="variants", on_delete=models.CASCADE)
    color = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to="variants/", blank=True, null=True)

    def __str__(self):
        return f"Variant of {self.advert.title}"



class ShopImage(models.Model):
    shop = models.ForeignKey("Shop", related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="shops/")

    def __str__(self):
        return f"Image for {self.shop.shop_name}"