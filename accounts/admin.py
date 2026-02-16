from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'phone_number')}),
    )  # add fieldsets later if you add extra fields


add_fieldsets = UserAdmin.add_fieldsets + (
    (None, {'fields': ('role', 'phone_number')}),
)


