from django.urls import path

from hub.views import index, select_collection, CardListView, CardDetailView

urlpatterns = [
    path("", index, name="index"),
    path("select_collection/", select_collection, name="select-collection"),
    path("cards/", CardListView.as_view(), name="card-list"),
    path("cards/<int:pk>/", CardDetailView.as_view(), name="card-detail"),

]

app_name = "hub"
