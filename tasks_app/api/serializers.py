from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import Task


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']

    def get_full_name(self, obj):
        return obj.userprofile.full_name


class TaskSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee', queryset=User.objects.all(), required=False, write_only=True, allow_null=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer', queryset=User.objects.all(), required=False, write_only=True, allow_null=True)
    comments_count = serializers.SerializerMethodField()
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'assignee',
                  'reviewer', 'due_date', 'comments_count', 'assignee_id', 'reviewer_id']

    def get_comments_count(self, obj):
        # return obj.comments.count()
        return 0

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and request.method == "PATCH":
            data.pop("comments_count", None)
        return data

    def validate(self, attrs):
        board = self._get_board(attrs)

        self._validate_user_role(attrs.get('assignee'), board, 'Assignee')
        self._validate_user_role(attrs.get('reviewer'), board, 'Reviewer')

        self._prevent_board_change(attrs)

        return attrs

    def _get_board(self, attrs):
        board = attrs.get('board')
        if board is not None:
            return board
        instance = getattr(self, 'instance', None)
        if instance is not None:
            return instance.board
        raise serializers.ValidationError({"board": "Board must be provided."}
                                          )

    def _validate_user_role(self, user, board, role_name):
        if user is None:
            return

        if not board.members.filter(id=user.id).exists():
            raise serializers.ValidationError(
                {role_name.lower(): f"{role_name} must be Member of Board."}
            )

    def _prevent_board_change(self, attrs):
        instance = getattr(self, 'instance', None)
        if instance is None:
            return

        if 'board' in attrs and attrs['board'] != instance.board:
            raise serializers.ValidationError(
                {"board": "Changing the board of a task is not allowed."}
            )
