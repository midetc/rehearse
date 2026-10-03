from django.core.management.base import BaseCommand

from hub.catalog_seed import CATALOG
from hub.models import CardTemplate, Category, Collection


class Command(BaseCommand):
    help = "Load interview collections, categories, and card templates"

    def handle(self, *args, **options):
        collections = 0
        categories = 0
        templates = 0
        pruned = 0
        active_slugs = {item["slug"] for item in CATALOG}

        for item in CATALOG:
            collection, created = Collection.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "name": item["name"],
                    "description": item.get("description", ""),
                    "is_active": True,
                },
            )
            collections += int(created)
            keep_category_names = {cat["name"] for cat in item["categories"]}

            for cat in item["categories"]:
                category, cat_created = Category.objects.update_or_create(
                    collection=collection,
                    name=cat["name"],
                    defaults={"description": cat.get("description", "")},
                )
                categories += int(cat_created)
                keep_questions = set()

                for card in cat["cards"]:
                    keep_questions.add(card["question"])
                    _, tpl_created = CardTemplate.objects.update_or_create(
                        category=category,
                        question=card["question"],
                        defaults={
                            "answer": card["answer"],
                            "level": card["level"],
                        },
                    )
                    templates += int(tpl_created)

                deleted, _ = (
                    CardTemplate.objects.filter(category=category)
                    .exclude(question__in=keep_questions)
                    .delete()
                )
                pruned += deleted

            stale_categories = Category.objects.filter(
                collection=collection
            ).exclude(name__in=keep_category_names)
            for stale in stale_categories:
                deleted, _ = CardTemplate.objects.filter(category=stale).delete()
                pruned += deleted
                stale.delete()

        deactivated = Collection.objects.exclude(slug__in=active_slugs).filter(
            is_active=True
        ).update(is_active=False)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. new collections={collections}, "
                f"new categories={categories}, new templates={templates}, "
                f"pruned={pruned}, deactivated_old={deactivated}"
            )
        )
