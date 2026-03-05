from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    # Show these columns in admin list view
    list_display = ("username", "email", "role", "restaurant", "is_staff")

    # Fields when editing a user
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {
            "fields": ("role", "restaurant"),
        }),
    )

    # Fields when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {
            "fields": ("role", "restaurant"),
        }),
    )

    search_fields = ("username", "email")
