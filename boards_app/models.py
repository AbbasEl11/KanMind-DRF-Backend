"""
Board app models.

This module defines the Board model for Kanban board management.
"""

from django.contrib.auth.models import User
from django.db import models


class Board(models.Model):
    """
    Kanban board model.
    
    Represents a collaborative board that can contain tasks. Each board has
    an owner and can have multiple members who can collaborate on tasks.
    
    Attributes:
        title (str): The board's title/name (max 200 characters)
        owner (User): The user who created and owns the board
        members (ManyToMany): Users who have access to collaborate on the board
        
    Related Names:
        boards: Reverse relation from User to owned boards
        member_boards: Reverse relation from User to boards where user is a member
    """
    
    title = models.CharField(
        max_length=200,
        help_text="Board title/name"
    )
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='boards',
        help_text="Board owner/creator"
    )
    members = models.ManyToManyField(
        User, 
        related_name='member_boards', 
        blank=True,
        help_text="Users who can collaborate on this board"
    )

    def __str__(self):
        """Return string representation of the board."""
        return f'{self.title}'
    
    class Meta:
        verbose_name = "Board"
        verbose_name_plural = "Boards"
        ordering = ['-id']
