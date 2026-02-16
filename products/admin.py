from symtable import Class

from django.contrib import admin
from .models import Product, Offer
from django.contrib import admin
from .models import Offer
from messaging.models import Notification
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "category")

class OfferAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount')


admin.site.register(Product, ProductAdmin)
admin.site.register(Offer, OfferAdmin)

class OfferAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:  # Only when new offer is created
            # Send notification to all users (you can filter who should get it)
            for user in User.objects.all():
                Notification.objects.create(
                    user=user,
                    message=f"🎉 New offer available: {obj.code} - {obj.description}",
                    content_type=ContentType.objects.get_for_model(obj),
                    object_id=obj.id
                )