from django.contrib import admin

from hub.models import Collection, Category


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "collection")
