from django.shortcuts import render
from rest_framework import viewsets, mixins
from ..models import Task
from .serializers import TaskSerializer
from .permissions import IsMemberOfBoard, IsBoardOwner, IsTaskOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
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


class TaskCommentsViewSet(viewsets.ModelViewSet):
    pass


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
