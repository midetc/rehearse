from django.urls import path

from hub.views import index, select_collection, CardListView, CardDetailView, \
    CardCreateView, CardUpdateView

urlpatterns = [
    path("", index, name="index"),
    path("select_collection/", select_collection, name="select-collection"),
    path("cards/", CardListView.as_view(), name="card-list"),
    path("cards/<int:pk>/", CardDetailView.as_view(), name="card-detail"),
    path("cards/create/", CardCreateView.as_view(), name="card-create"),
    path("cards/<int:pk>/update", CardUpdateView.as_view(),
         name="card-update"),

]

app_name = "hub"
