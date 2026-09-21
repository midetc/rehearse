from django.contrib.auth.models import AbstractUser
from django.db import models

from hub.models import Collection


class User(AbstractUser):
    active_collection = models.ForeignKey(
        Collection, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.username
