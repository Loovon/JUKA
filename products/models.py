from django.db import models
from django.conf import settings





class Product(models.Model):
    category = models.ForeignKey("categories.Category", related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/")
    type = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    thickness = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.CharField(max_length=50, blank=True, null=True)  # <-- new
    shape = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class Offer(models.Model):
    code = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    discount = models.FloatField()

    def __str__(self):
        return self.code

    def get_absolute_url(self):
        return reverse("offer_detail", args=[self.id])

