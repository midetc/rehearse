from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render

def index(request: HttpRequest) -> HttpResponse:

    return render(request, 'hub/index.html')