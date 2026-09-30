from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView

from hub.filters import CardFilter
from hub.forms import SelectCollectionForm, CardQuestionSearchForm
from hub.models import Card, CardTemplate, Category


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
        queryset = super().get_queryset().filter(owner=self.request.user,
                                                 category__collection=self.request.user.active_collection)
        question = self.request.GET.get("question")

        if question:
            queryset = queryset.filter(question__icontains=question)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        question = self.request.GET.get("question", "")

        context["search_form"] = CardQuestionSearchForm(
            initial={"question": question})

        context["filter"] = CardFilter(
            self.request.GET,
            queryset=self.get_queryset(),
            request=self.request,
        )

        return context


class CardDetailView(LoginRequiredMixin, DetailView):
    model = Card

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user,
                                             category__collection=self.request.user.active_collection).select_related(
            "category", "category__collection"
        )


class CardCreateView(LoginRequiredMixin, CreateView):
    model = Card
    fields = ["level", "category", "question", "answer", "status"]
    success_url = reverse_lazy("hub:card-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.is_custom = True
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["category"].queryset = Category.objects.filter(
            collection_id=self.request.user.active_collection_id
        )
        return form


class CardUpdateView(LoginRequiredMixin, UpdateView):
    model = Card
    fields = ["level", "category", "question", "answer", "status"]

    success_url = reverse_lazy("hub:card-list")

    def get_queryset(self):
        return super().get_queryset().filter(
            owner=self.request.user,
            category__collection=self.request.user.active_collection,
        )

    def form_valid(self, form):
        if not form.instance.is_custom:
            form.instance.is_custom = True
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["category"].queryset = Category.objects.filter(
            collection_id=self.request.user.active_collection_id
        )
        return form


class CardDeleteView(LoginRequiredMixin, DeleteView):
    model = Card
    template_name = "hub/card_confirm_delete.html"
    success_url = reverse_lazy("hub:card-list")

    def get_queryset(self):
        return super().get_queryset().filter(
            owner=self.request.user,
            category__collection=self.request.user.active_collection,
        )
