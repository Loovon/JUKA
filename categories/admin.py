from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")   # show ID and Name in the admin list
    search_fields = ("name",)       # allow searching by name
