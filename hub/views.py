from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render

@login_required
def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'hub/index.html')