from rest_framework.permissions import BasePermission, SAFE_METHODS
from boards_app.models import Board
from tasks_app.models import Task


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):

        return obj.board.owner == request.user


class IsMemberOfBoard(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        board = obj.board
        return board.members.filter(id=request.user.id).exists()


class IsTaskOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.assignee_id == request.user

class IsCreatorOfComment(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user