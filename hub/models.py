from django.conf import settings
from django.db import models



class Collection(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}, (is_active={self.is_active})"


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.collection})"

class Level(models.TextChoices):
    JUNIOR = "junior", "Junior"
    MIDDLE = "middle", "Middle"
    SENIOR = "senior", "Senior"

class CardTemplate(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    level = models.CharField(
        max_length=20,
        choices=Level.choices,

    )
    question = models.TextField()
    answer = models.TextField()


class Card(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        LEARNING = "learning", "Learning"
        KNOWN = "known", "Known"
        MASTERED  = "mastered", "Mastered"
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    template = models.ForeignKey(
        CardTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )
    is_custom = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    level = models.CharField(
        max_length=20,
        choices=Level.choices,

    )
    question = models.TextField()
    answer = models.TextField()