# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    @property
    def is_buyer(self):
        return self.role == 'buyer'

    @property
    def is_seller(self):
        return self.role == 'seller'





def __str__(self):
    return self.username

# Create your models here.
