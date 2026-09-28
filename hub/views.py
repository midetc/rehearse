from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from hub.forms import SelectCollectionForm
from hub.models import Card, CardTemplate


@login_required
def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'hub/index.html')


@login_required
def select_collection(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SelectCollectionForm(request.POST)

        if form.is_valid():
            request.user.active_collection = form.cleaned_data["collection"]
            request.user.save()

            if not Card.objects.filter(
                    category__collection=request.user.active_collection,
                    owner=request.user
            ).exists():
                seed_cards_for_user(request.user)
            return redirect("hub:index")
    else:
        form = SelectCollectionForm(
            initial={"collection": request.user.active_collection})

    return render(request, "hub/select_collection.html",
                  context={"form": form})


User = get_user_model()


def seed_cards_for_user(user: User) -> None:
    card_templates = CardTemplate.objects.filter(
        category__collection=user.active_collection
    )
    cards = [
        Card(
            owner=user,
            template=card_template,
            status=Card.Status.NEW,
            category=card_template.category,
            level=card_template.level,
            question=card_template.question,
            answer=card_template.answer,
        )
        for card_template in card_templates
    ]
    Card.objects.bulk_create(cards)


class CardListView(LoginRequiredMixin, ListView):
    model = Card

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user, category__collection=self.request.user.active_collection)


class CardDetailView(LoginRequiredMixin, DetailView):
    model = Card

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user, category__collection=self.request.user.active_collection)