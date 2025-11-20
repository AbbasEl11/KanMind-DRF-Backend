"""
Task API permissions.

This module defines custom permission classes for task-level access control.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBoardOwner(BasePermission):
    """
    Permission check: user is the board owner.
    
    Object-level permission that grants access only if the requesting user
    owns the board that contains the task.
    
    Used for:
        - Creating tasks (board owner only)
        - Deleting tasks (board owner or task assignee)
    """
    
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


class IsMemberOfBoard(BasePermission):
    """
    Permission check: user is a member of the board.
    
    Object-level permission that grants read access to anyone,
    but write access only to board members.
    
    Used for:
        - Updating tasks (board members can update)
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is a member of the task's board.
        
        Safe methods (GET, HEAD, OPTIONS) are allowed for all.
        Unsafe methods require board membership.
        
        Args:
            request: HTTP request
            view: View being accessed
            obj (Task): Task instance being accessed
            
        Returns:
            bool: True if safe method or user is board member, False otherwise
        """
        # Allow read-only methods for all authenticated users
        if request.method in SAFE_METHODS:
            return True
            
        # Write operations require board membership
        board = obj.board
        return board.members.filter(id=request.user.id).exists()


class IsTaskOwner(BasePermission):
    """
    Permission check: user is the task assignee.
    
    Object-level permission that grants access only if the requesting user
    is assigned to the task.
    
    Used for:
        - Deleting tasks (task assignee can delete their own tasks)
    """
    
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