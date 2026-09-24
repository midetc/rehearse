from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render, redirect

from hub.forms import SelectCollectionForm


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
            return redirect("hub:index")
    else:
        form = SelectCollectionForm(
            initial={"collection": request.user.active_collection})

    return render(request, "hub/select_collection.html",
                  context={"form": form})
