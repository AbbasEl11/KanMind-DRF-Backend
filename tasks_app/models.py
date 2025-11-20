"""
Task app models.

This module defines models for task management and task comments within boards.
"""

from django.contrib.auth.models import User
from django.db import models
from boards_app.models import Board


def choices_status():
    """
    Return available task status choices.
    
    Returns:
        list: Task status options
    """
    status = ["to-do", "in-progress", "review", "done"]
    return status


def choices_priority():
    """
    Return available task priority choices.
    
    Returns:
        list: Task priority levels
    """
    priority = ["low", "medium", "high"]
    return priority


class Task(models.Model):
    """
    Task model for Kanban boards.
    
    Represents a task/ticket on a board with status tracking, priority levels,
    assignment capabilities, and due dates.
    
    Attributes:
        board (Board): The board this task belongs to
        title (str): Task title/summary (max 200 characters)
        description (str): Detailed task description (optional)
        status (str): Current task status (to-do, in-progress, review, done)
        priority (str): Task priority level (low, medium, high)
        assignee (User): User responsible for completing the task (optional)
        reviewer (User): User responsible for reviewing the task (optional)
        due_date (date): Task deadline (optional)
        
    Related Names:
        assignee: Reverse relation from User to assigned tasks
        reviewer: Reverse relation from User to tasks under review
    """
    
    board = models.ForeignKey(
        Board, 
        on_delete=models.CASCADE,
        help_text="Board this task belongs to"
    )
    title = models.CharField(
        max_length=200,
        help_text="Task title/summary"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed task description"
    )
    status = models.CharField(
        max_length=50, 
        choices=[(status, status) for status in choices_status()], 
        default="to-do",
        help_text="Current task status"
    )
    priority = models.CharField(
        max_length=50, 
        choices=[(priority, priority) for priority in choices_priority()], 
        default="medium",
        help_text="Task priority level"
    )
    assignee = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assignee',
        help_text="User assigned to complete this task"
    )
    reviewer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewer',
        help_text="User assigned to review this task"
    )
    due_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Task deadline"
    )
    
    def __str__(self):
        """Return string representation of the task."""
        return f'{self.title}'
    
    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-id']


class TaskComment(models.Model):
    """
    Comment model for tasks.
    
    Allows users to add comments/notes to tasks for collaboration and discussion.
    
    Attributes:
        task (Task): The task this comment belongs to
        author (User): The user who created the comment
        content (str): The comment text content
        created_at (datetime): Timestamp when comment was created (auto-generated)
        
    Related Names:
        comments: Reverse relation from Task to its comments
    """
    
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='comments',
        help_text="Task this comment belongs to"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        help_text="Comment author"
    )
    content = models.TextField(
        help_text="Comment content"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Comment creation timestamp"
    )
    
    def __str__(self):
        """Return string representation of the comment."""
        return f'Comment by {self.author.username} on {self.task.title}'
    
    class Meta:
        verbose_name = "Task Comment"
        verbose_name_plural = "Task Comments"
        ordering = ['created_at']