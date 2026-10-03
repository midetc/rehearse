from django.urls import path

from hub.views import index, select_collection, CardListView, CardDetailView, \
    CardCreateView, CardUpdateView, CardDeleteView, card_set_status, \
    practice_menu, practice_start, practice_card, reset_cards

urlpatterns = [
    path("", index, name="index"),
    path("select_collection/", select_collection, name="select-collection"),
    path("cards/", CardListView.as_view(), name="card-list"),
    path("cards/<int:pk>/", CardDetailView.as_view(), name="card-detail"),
    path("cards/create/", CardCreateView.as_view(), name="card-create"),
    path("cards/<int:pk>/update/", CardUpdateView.as_view(),
         name="card-update"),
    path("cards/<int:pk>/delete/", CardDeleteView.as_view(),
         name="card-delete"),
    path(
        "cards/<int:pk>/status/",
        card_set_status,
        name="card-set-status",
    ),
    path("practice/", practice_menu, name="practice-menu"),
    path("practice/run/", practice_start, name="practice-start"),
    path("practice/run/<int:pk>/", practice_card, name="practice-card"),
    path(
        "cards/reset-cards/",
        reset_cards,
        name="reset-cards",
    ),
]

app_name = "hub"
