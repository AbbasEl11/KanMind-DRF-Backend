from rest_framework.permissions import BasePermission


class IsBoardMemberOrOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user in obj.members.all()

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsBoardOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
