from django.forms import CharField, Form, ModelForm, TextInput

from hub.models import Card


class CardQuestionSearchForm(Form):
    question = CharField(max_length=255, required=False)


class CardForm(ModelForm):
    topic = CharField(
        max_length=200,
        required=False,
        label="Topic",
        widget=TextInput(attrs={"placeholder": "For example, Python decorators"}),
    )

    class Meta:
        model = Card
        fields = ["level", "category", "question", "answer"]
