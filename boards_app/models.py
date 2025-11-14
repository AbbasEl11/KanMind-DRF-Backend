from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Board(models.Model):
    title = models.CharField(max_length=200)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='boards')
    members = models.ManyToManyField(
        User, related_name='member_boards', blank=True)

    def __str__(self):
        return self.title
