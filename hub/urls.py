from django.urls import path

from hub.views import index, select_collection, CardListView, CardDetailView, \
    CardCreateView

urlpatterns = [
    path("", index, name="index"),
    path("select_collection/", select_collection, name="select-collection"),
    path("cards/", CardListView.as_view(), name="card-list"),
    path("cards/<int:pk>/", CardDetailView.as_view(), name="card-detail"),
    path("cards/create/", CardCreateView.as_view(), name="card-create"),

]

app_name = "hub"
