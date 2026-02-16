# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from ..customers.models import CustomerProfile
from ..sellers.models import SellerProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'buyer':
            CustomerProfile.objects.create(user=instance)
        elif instance.role == 'seller':
            SellerProfile.objects.create(user=instance)
