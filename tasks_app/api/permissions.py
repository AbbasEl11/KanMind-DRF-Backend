"""
Task API permissions.

This module defines custom permission classes for task-level access control.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import NotFound


class IsBoardOwnerOrMember(BasePermission):
    """
    Permission check: user is the board owner or member.

    Permission that grants access if the requesting user is either
    the board owner or a member of the board.

    Used for:
        - Creating tasks (owner or members can create)
    """

    message = "You must be the board owner or a member to perform this action."

    def has_permission(self, request, view):
        """
        Check if user is authenticated and (for create) is board owner or member.

        For create actions, validates board ownership or membership from request data.
        For other actions, only checks authentication.
        """
        if not (request.user and request.user.is_authenticated):
            return False

        if view.action == 'create':
            from boards_app.models import Board
            board_id = request.data.get('board')

            if not board_id:
                return False

            try:
                board = Board.objects.get(pk=board_id)
                return board.owner == request.user or request.user in board.members.all()
            except Board.DoesNotExist:
                raise NotFound(detail="Board with this ID does not exist.")

        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if user is owner or member of the task's board.

        Args:
            request: HTTP request
            view: View being accessed
            obj (Task): Task instance being accessed

        Returns:
            bool: True if user is owner or member, False otherwise
        """
        board = obj.board
        return board.owner == request.user or request.user in board.members.all()


class IsBoardOwner(BasePermission):
    """
    Permission check: user is the board owner.

    Object-level permission that grants access only if the requesting user
    owns the board that contains the task.

    Used for:

        - Deleting tasks (board owner or task assignee)
    """

    message = "Only the board owner can perform this action."

    def has_permission(self, request, view):
        """
        Check if user is authenticated and (for create) is board owner.

        For create actions, validates board ownership from request data.
        For other actions, only checks authentication.
        """
        if not (request.user and request.user.is_authenticated):
            return False
        if view.action == 'create':
            from boards_app.models import Board
            board_id = request.data.get('board')

            if not board_id:
                return False

            try:
                board = Board.objects.get(pk=board_id)
                return board.owner == request.user
            except Board.DoesNotExist:
                return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if user owns the task's board.

        Args:
            request: HTTP request
            view: View being accessed
            obj (Task): Task instance being accessed

        Returns:
            bool: True if user owns the board, False otherwise
        """
        return obj.board.owner == request.user


class IsTaskOwner(BasePermission):
    """
    Permission check: user is the task assignee.

    Object-level permission that grants access only if the requesting user
    is assigned to the task.

    Used for:
        - Creating tasks (board owner only)
        - Deleting tasks (task assignee can delete their own tasks)
    """

    message = "Only the task assignee can perform this action."

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if user is assigned to the task.

        Args:
            request: HTTP request
            view: View being accessed
            obj (Task): Task instance being accessed

        Returns:
            bool: True if user is task assignee, False otherwise
        """
        return obj.assignee_id == request.user


class IsCreatorOfComment(BasePermission):
    """
    Permission check: user is the comment author.

    Object-level permission that grants access only if the requesting user
    created the comment.

    Used for:
        - Deleting comments (authors can delete their own comments)
        - Updating comments (if implemented)
    """

    message = "Only the comment author can perform this action."

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if user authored the comment.

        Args:
            request: HTTP request
            view: View being accessed
            obj (TaskComment): Comment instance being accessed

        Returns:
            bool: True if user is comment author, False otherwise
        """
        return obj.author == request.user
