"""
Board API permissions.

This module defines custom permission classes for board-level access control.
"""

from rest_framework.permissions import BasePermission


class IsBoardMemberOrOwner(BasePermission):
    """
    Permission check: user is board owner or member.

    Object-level permission that grants access if the requesting user
    is either the board owner or listed as a board member.

    Used for:
        - Viewing board details
        - Updating board (combined with ownership checks)
        - Accessing board-related resources
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if user is owner or member of the board.

        Args:
            request: HTTP request
            view: View being accessed
            obj (Board): Board instance being accessed

        Returns:
            bool: True if user is owner or member, False otherwise
        """
        return obj.owner == request.user or request.user in obj.members.all()

    def has_permission(self, request, view):
        """
        Check if user is authenticated.

        Args:
            request: HTTP request
            view: View being accessed

        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return request.user and request.user.is_authenticated


class IsBoardOwner(BasePermission):
    """
    Permission check: user is board owner.

    Object-level permission that grants access only to the board owner.
    More restrictive than IsBoardMemberOrOwner.

    Used for:
        - Deleting boards
        - Critical board management operations
    """

    message = "Only the board owner can perform this action."

    def has_object_permission(self, request, view, obj):
        """
        Check if user is the board owner.

        Args:
            request: HTTP request
            view: View being accessed
            obj (Board): Board instance being accessed

        Returns:
            bool: True if user is owner, False otherwise
        """
        return obj.owner == request.user
