from django.contrib import admin

from hub.models import Collection, Category, CardTemplate, Card


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "collection")


@admin.register(CardTemplate)
class CardTemplateAdmin(admin.ModelAdmin):
    list_display = ("category", "level", "question", "answer")


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("owner", "template", "status", "is_custom", "created_at", "updated_at")

