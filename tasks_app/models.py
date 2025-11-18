from django.db import models
from django.contrib.auth.models import User
from boards_app.models import Board
# Create your models here.


def choices_status():
    status = ["to-do", "in-progress", "review", "done"]
    return status


def choices_priority():
    priority = ["low", "medium", "high"]
    return priority


class Task(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=[(
        status, status) for status in choices_status()], default="to-do")
    priority = models.CharField(max_length=50, choices=[(
        priority, priority) for priority in choices_priority()], default="medium")
    assignee = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignee')
    reviewer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewer')
    due_date = models.DateField(null=True, blank=True)


class TaskComment(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)