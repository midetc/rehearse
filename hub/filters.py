from django_filters import FilterSet

from hub.models import Card, Category


class CardFilter(FilterSet):
    class Meta:
        model = Card
        fields = ["category", "level", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = getattr(self.request, "user", None)
        if user is not None and user.active_collection_id:
            self.filters["category"].queryset = Category.objects.filter(
                collection_id=user.active_collection_id
            )
