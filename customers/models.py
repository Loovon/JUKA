# customers/models.py
from django.db import models
from django.conf import settings
from products.models import Product
from sellers.models import Advert
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator



class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    loyalty_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Customer: {self.user.username}"


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    advert = models.ForeignKey("sellers.Advert", on_delete=models.CASCADE)  # switched from Product → Advert
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'advert')  # avoid duplicate entries

    def __str__(self):
        return f"{self.user.username} - {self.advert.title} ({self.quantity})"

    def subtotal(self):
        return self.advert.price * self.quantity


class SavedItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    advert = models.ForeignKey("sellers.Advert", on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'advert')  # avoid duplicates

    def __str__(self):
        return f"{self.user.username} saved {self.advert.title}"


@receiver(post_save, sender=CustomUser)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.get_or_create(user=instance)


class Review(models.Model):
    advert = models.ForeignKey(Advert, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    image = models.ImageField(upload_to="review_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} review on {self.advert.title}"