from django.urls import path

from hub.views import index

urlpatterns = [
    path("", index, name="index"),
]

app_name = "hub"
