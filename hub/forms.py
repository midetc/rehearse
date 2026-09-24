from django.forms import ModelChoiceField, Form

from hub.models import Collection


class SelectCollectionForm(Form):
    collection = ModelChoiceField(
        queryset=Collection.objects.filter(is_active=True),
    )
