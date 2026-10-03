from django.contrib.auth import login
from django.db import IntegrityError, transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import SignUpForm


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("hub:select-collection")

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save()
        except IntegrityError:
            form.add_error(
                "username",
                "A user with that username already exists.",
            )
            return self.form_invalid(form)
        login(self.request, self.object)
        return redirect(self.get_success_url())
