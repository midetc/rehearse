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


