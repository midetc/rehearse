from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, QuerySet
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView

from hub.catalog_seed import ICON_LABELS
from hub.filters import CardFilter
from hub.forms import CardQuestionSearchForm
from hub.models import Card, CardTemplate, Category, Collection


class ActiveCollectionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.active_collection_id:
            return redirect("hub:select-collection")
        return super().dispatch(request, *args, **kwargs)


@login_required
def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'hub/index.html')


@login_required
def select_collection(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        collection = get_object_or_404(
            Collection,
            pk=request.POST.get("collection"),
            is_active=True,
        )
        request.user.active_collection = collection
        request.user.save()
        if not Card.objects.filter(
            category__collection=collection,
            owner=request.user,
        ).exists():
            seed_cards_for_user(request.user)
        return redirect("hub:index")

    collections = (
        Collection.objects.filter(is_active=True)
        .annotate(
            topic_count=Count("category", distinct=True),
            card_count=Count("category__cardtemplate", distinct=True),
        )
        .order_by("name")
    )
    tracks = []
    for collection in collections:
        owned = Card.objects.filter(
            owner=request.user,
            category__collection=collection,
        )
        total = owned.count()
        done = owned.filter(
            status__in=[Card.Status.KNOWN, Card.Status.MASTERED]
        ).count()
        progress = int((done / total) * 100) if total else None
        tracks.append(
            {
                "id": collection.id,
                "name": collection.name,
                "slug": collection.slug,
                "description": collection.description,
                "icon": ICON_LABELS.get(
                    collection.slug, collection.name[:2].upper()
                ),
                "topic_count": collection.topic_count,
                "card_count": collection.card_count,
                "progress": progress,
                "is_current": collection.id == request.user.active_collection_id,
            }
        )
    return render(
        request,
        "hub/select_collection.html",
        {"tracks": tracks, "track_count": len(tracks)},
    )


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


class CardListView(LoginRequiredMixin, ActiveCollectionRequiredMixin, ListView):
    model = Card
    paginate_by = 20
    context_object_name = "cards"

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(
                owner=self.request.user,
                category__collection=self.request.user.active_collection,
            )
            .select_related("category")
            .order_by("id")
        )
        question = self.request.GET.get("question")
        if question:
            queryset = queryset.filter(question__icontains=question)
        self.filterset = CardFilter(
            self.request.GET,
            queryset=queryset,
            request=self.request,
        )
        return self.filterset.qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.request.GET.get("question", "")
        context["search_form"] = CardQuestionSearchForm(
            initial={"question": question}
        )
        context["filter"] = self.filterset
        params = self.request.GET.copy()
        params.pop("page", None)
        context["querystring"] = params.urlencode()
        return context


class CardDetailView(LoginRequiredMixin, ActiveCollectionRequiredMixin, DetailView):
    model = Card

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user,
                                             category__collection=self.request.user.active_collection).select_related(
            "category", "category__collection"
        )


class CardCreateView(LoginRequiredMixin, ActiveCollectionRequiredMixin, CreateView):
    model = Card
    fields = ["level", "category", "question", "answer"]
    success_url = reverse_lazy("hub:card-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.is_custom = True
        form.instance.status = Card.Status.NEW
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["category"].queryset = Category.objects.filter(
            collection_id=self.request.user.active_collection_id
        )
        return form


class CardUpdateView(LoginRequiredMixin, ActiveCollectionRequiredMixin, UpdateView):
    model = Card
    fields = ["level", "category", "question", "answer"]

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


class CardDeleteView(LoginRequiredMixin, ActiveCollectionRequiredMixin, DeleteView):
    model = Card
    template_name = "hub/card_confirm_delete.html"
    success_url = reverse_lazy("hub:card-list")

    def get_queryset(self):
        return super().get_queryset().filter(
            owner=self.request.user,
            category__collection=self.request.user.active_collection,
        )


@login_required
@require_POST
def card_set_status(request: HttpRequest, pk: int) -> HttpResponse:
    if not request.user.active_collection_id:
        return redirect("hub:select-collection")
    card = get_object_or_404(
        Card.objects.filter(
            owner=request.user,
            category__collection_id=request.user.active_collection_id,
        ),
        pk=pk,
    )
    action = request.POST.get("action")
    if action == "know":
        if card.status == Card.Status.NEW:
            card.status = Card.Status.KNOWN
        elif card.status == Card.Status.LEARNING:
            card.status = Card.Status.MASTERED
    elif action == "dont_know":
        card.status = Card.Status.LEARNING
    else:
        return redirect("hub:card-detail", pk=pk)

    card.save(update_fields=["status", "updated_at"])

    next_url = request.POST.get("next")
    mode = request.POST.get("mode", "")
    if next_url == "practice":
        nxt = _next_practice_card(request.user, mode, card.pk)
        if nxt is None:
            return redirect(
                f"{reverse('hub:practice-menu')}?done=1&mode={mode}")
        return redirect(
            f"{reverse('hub:practice-card', kwargs={'pk': nxt.pk})}?mode={mode}"
        )

    return redirect("hub:card-detail", pk=pk)


def _user_cards(user) -> QuerySet:
    return Card.objects.filter(
        owner=user,
        category__collection_id=user.active_collection_id,
    )


def _practice_queue(user, mode: str) -> QuerySet:
    qs = _user_cards(user).order_by("id")
    if mode == "new":
        return qs.filter(status=Card.Status.NEW)
    if mode == "learning":
        return qs.filter(status=Card.Status.LEARNING)
    if mode == "all":
        return qs.filter(
            status__in=[Card.Status.NEW, Card.Status.LEARNING]
        )
    return qs.none()

def _next_practice_card(user, mode: str, current_pk: int):
    qs = _practice_queue(user, mode).exclude(pk=current_pk)
    return qs.first()


@login_required
def practice_menu(request: HttpRequest) -> HttpResponse:
    if not request.user.active_collection_id:
        return redirect("hub:select-collection")
    return render(request, "hub/practice_menu.html")


@login_required
def practice_start(request: HttpRequest) -> HttpResponse:
    if not request.user.active_collection_id:
        return redirect("hub:select-collection")
    mode = request.GET.get("mode", "")
    queue = _practice_queue(request.user, mode)
    pks = list(queue.values_list("pk", flat=True))
    request.session["practice_mode"] = mode
    request.session["practice_pks"] = pks
    card = queue.first()
    if card is None:
        return render(
            request,
            "hub/practice_done.html",
            {"mode": mode},
        )
    return redirect(
        f"{reverse('hub:practice-card', kwargs={'pk': card.pk})}?mode={mode}")


@login_required
def practice_card(request: HttpRequest, pk: int) -> HttpResponse:
    if not request.user.active_collection_id:
        return redirect("hub:select-collection")
    mode = request.GET.get("mode", "")
    pks = request.session.get("practice_pks", [])
    mode = request.session.get("practice_mode", mode)


    card = get_object_or_404(
        _user_cards(request.user).select_related(
            "category", "category__collection"
        ),
        pk=pk,
    )
    if card.pk not in pks:
        return redirect("hub:practice-menu")
    total = len(pks)
    position = pks.index(card.pk) + 1
    return render(
        request,
        "hub/practice_card.html",
        {"card": card, "mode": mode, "position": position, "total": total},
    )

@login_required
def reset_cards(request: HttpRequest) -> HttpResponse:
    if not request.user.active_collection_id:
        return redirect("hub:select-collection")

    if request.method == "POST":
        Card.objects.filter(
            owner=request.user,
            category__collection_id=request.user.active_collection_id,
        ).delete()
        seed_cards_for_user(request.user)
        request.session.pop("practice_pks", None)
        request.session.pop("practice_mode", None)
        return redirect("hub:card-list")

    return render(request, "hub/reset_cards_confirm.html")