from django.urls import path

from hub.views import index, select_collection

urlpatterns = [
    path("", index, name="index"),
    path("select_collection/", select_collection, name="select-collection"),
]

app_name = "hub"
