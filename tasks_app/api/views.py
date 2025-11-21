"""
Task API views.

This module contains view classes for task and task comment management,
including filtered task views for assigned and reviewing tasks.
"""

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Task, TaskComment
from .serializers import TaskSerializer, TaskCommentSerializer
from .permissions import IsBoardOwner, IsTaskOwner, IsBoardOwnerOrMember


class TaskViewSet(mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint for task management.

    Provides create, update, and delete operations for tasks.
    Uses dynamic permissions based on action.

    Endpoints:
        POST /api/tasks/ - Create new task
        PUT/PATCH /api/tasks/{id}/ - Update task
        DELETE /api/tasks/{id}/ - Delete task

    Permissions:
        - Create: IsBoardOwner (only board owner can create tasks)
        - Update: IsMemberOfBoard (board members can update tasks)
        - Delete: IsBoardOwner | IsTaskOwner (owner or assignee can delete)
    """

    queryset = Task.objects.all()
    lookup_field = 'pk'
    serializer_class = TaskSerializer

    def get_permissions(self):
        """
        Return appropriate permissions based on action.

        Returns:
            list: Permission instances for current action
        """
        if self.action == 'create':
            permission_classes = [IsBoardOwnerOrMember]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsBoardOwnerOrMember]
        elif self.action == 'destroy':
            permission_classes = [IsBoardOwner | IsTaskOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class TaskCommentsViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """
    API endpoint for task comment management.

    Nested under tasks. Provides list, create, and delete operations.
    Only board members can access comments.

    Endpoints:
        GET /api/tasks/{task_id}/comments/ - List task comments
        POST /api/tasks/{task_id}/comments/ - Create comment
        DELETE /api/tasks/{task_id}/comments/{id}/ - Delete comment

    Permissions:
        - List/Create: Board member or owner
        - Delete: Comment author only
    """

    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        """
        Return comments for the specified task.

        Only board members can view comments.

        Returns:
            QuerySet: Filtered comment queryset

        Raises:
            PermissionDenied: If user is not board member/owner
        """
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(
            Task.objects.select_related("board"), pk=task_id)
        user = self.request.user
        board = task.board

        # Verify user is board member or owner
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied(
                "You do not have permission to view comments for this task."
            )

        return TaskComment.objects.filter(task=task).select_related("author")

    def create(self, request, *args, **kwargs):
        """
        Create a new comment on a task.

        Args:
            request: HTTP request with comment data

        Returns:
            Response: Created comment data (201) or error (403)
        """
        task_id = kwargs.get('task_pk')
        task = get_object_or_404(
            Task.objects.select_related("board"), pk=task_id)
        user = request.user
        board = task.board

        # Verify user is board member or owner
        if user != board.owner and user not in board.members.all():
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=403
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, task=task)

        # Return formatted response
        response = {
            "id": serializer.instance.id,
            "author": user.userprofile.full_name,
            "content": serializer.instance.content,
            "created_at": serializer.instance.created_at
        }
        return Response(response, status=201)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a comment.

        Only comment authors can delete their own comments.

        Args:
            request: HTTP request

        Returns:
            Response: Empty response (204) or error (403)
        """
        comment = self.get_object()
        user = request.user

        # Verify user is comment author
        if comment.author != user:
            return Response(
                {'detail': 'You do not have permission to delete this comment.'},
                status=403
            )

        self.perform_destroy(comment)
        return Response(status=204)


class TaskAssignedOrReviewerViewSet(mixins.ListModelMixin,
                                    viewsets.GenericViewSet):
    """
    API endpoint for filtered task views.

    Provides filtered lists of tasks where the user is either
    the assignee or reviewer.

    Endpoints:
        GET /api/tasks/assigned-to-me/ - Tasks assigned to current user
        GET /api/tasks/reviewing/ - Tasks user is reviewing

    Permissions:
        - IsAuthenticated: User must be logged in
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    mode = None

    def get_dispatch(self, request, *args, **kwargs):
        """
        Store mode from URL kwargs before dispatch.

        Args:
            request: HTTP request

        Returns:
            Response: Dispatched view response
        """
        if 'mode' in kwargs:
            self.mode = kwargs.pop('mode')
        return super().get_dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return tasks based on mode (assigned or reviewer).

        Returns:
            QuerySet: Filtered task queryset
        """
        query_set = Task.objects.all()

        if self.mode == 'assigned':
            qs = query_set.filter(assignee=self.request.user)
        elif self.mode == 'reviewer':
            qs = query_set.filter(reviewer=self.request.user)

        return qs
