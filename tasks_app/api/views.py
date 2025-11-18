from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, mixins
from ..models import Task, TaskComment
from .serializers import TaskSerializer, TaskCommentSerializer
from .permissions import IsMemberOfBoard, IsBoardOwner, IsTaskOwner, IsCreatorOfComment
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied
# Create your views here.


class TaskViewSet(mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Task.objects.all()
    lookup_field = 'pk'
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsBoardOwner]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsMemberOfBoard]
        elif self.action == 'destroy':
            permission_classes = [IsBoardOwner | IsTaskOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class TaskCommentsViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    queryset = TaskComment.objects.all()   
    serializer_class = TaskCommentSerializer
    lookup_field = 'pk'
    
    
    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task.objects.select_related("board"), pk=task_id)
        user = self.request.user
        board = task.board
        
     
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("You do not have permission to view comments for this task.")
        
        return TaskComment.objects.filter(task=task).select_related("author")
    
    def create(self, request, *args, **kwargs):
        task_id = kwargs.get('task_pk')
        task = get_object_or_404(Task.objects.select_related("board"), pk=task_id)
        user = request.user
        board = task.board
        
        if user != board.owner and user not in board.members.all():
            return Response({'detail': 'You do not have permission to perform this action.'}, status=403)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, task=task)
        response={
            "id": serializer.instance.id,
            "author": user.userprofile.full_name,
            "content": serializer.instance.content,
            "created_at": serializer.instance.created_at
        }
        return Response(response, status=201)
    
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        user = request.user
        
        if comment.author != user:
            return Response({'detail': 'You do not have permission to delete this comment.'}, status=403)
        
        self.perform_destroy(comment)
        return Response(status=204)


class TaskAssignedOrReviewerViewSet(mixins.ListModelMixin,
                                    viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    mode = None

    def get_dispatch(self, request, *args, **kwargs):
        if 'mode' in kwargs:
            self.mode = kwargs.pop('mode')
        return super().get_dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query_set = Task.objects.all()
        if self.mode == 'assigned':
            qs = query_set.filter(assignee=self.request.user)
        elif self.mode == 'reviewer':
            qs = query_set.filter(reviewer=self.request.user)
        return qs
