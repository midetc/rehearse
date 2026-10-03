from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("active_collection",)
    fieldsets = UserAdmin.fieldsets + (
        (("Additional info", {"fields": ("active_collection",)}),)
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            (
                "Additional info",
                {"fields": ("active_collection",)},
            ),
        )
    )
