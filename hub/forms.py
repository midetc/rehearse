from django.forms import Form, CharField


class CardQuestionSearchForm(Form):
    question = CharField(max_length=255, required=False)
