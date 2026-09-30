from django.forms import ModelChoiceField, Form, CharField

from hub.models import Collection


class SelectCollectionForm(Form):
    collection = ModelChoiceField(
        queryset=Collection.objects.filter(is_active=True),
    )


class CardQuestionSearchForm(Form):
    question = CharField(max_length=255, required=False)
