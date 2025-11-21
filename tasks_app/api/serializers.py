"""
Task API serializers.

This module contains serializers for task and task comment management.
"""

from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import Task, TaskComment
from boards_app.models import Board


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user information in task context.

    Provides basic user details with full name from UserProfile.

    Fields:
        id (int): User unique identifier
        fullname (str): User's full display name
        email (str): User's email address
    """

    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'fullname', 'email']

    def get_fullname(self, obj):
        """Retrieve full name from associated UserProfile."""
        return obj.userprofile.full_name


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for task management.

    Handles task creation and updates with assignee/reviewer validation,
    ensuring they are board members. Prevents board changes after creation.

    Fields:
        id (int): Task unique identifier
        board (int): Board ID this task belongs to
        title (str): Task title/summary
        description (str): Detailed task description
        status (str): Task status (to-do, in-progress, review, done)
        priority (str): Task priority (low, medium, high)
        assignee (dict): Assignee user details (read-only)
        reviewer (dict): Reviewer user details (read-only)
        due_date (date): Task deadline
        comments_count (int): Number of comments on task
        assignee_id (int): Assignee user ID (write-only)
        reviewer_id (int): Reviewer user ID (write-only)
    """

    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all(),
        help_text="Board ID this task belongs to"
    )
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        allow_null=True,
        help_text="User ID to assign task to"
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        allow_null=True,
        help_text="User ID to assign as reviewer"
    )
    comments_count = serializers.SerializerMethodField()
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count',
            'assignee_id', 'reviewer_id'
        ]

    def get_comments_count(self, obj):
        """Return the number of comments on this task."""
        return obj.comments.count()

    def to_representation(self, instance):
        """
        Customize serialized output.

        Removes comments_count from PATCH responses to optimize payload.

        Args:
            instance (Task): Task instance to serialize

        Returns:
            dict: Serialized task data
        """
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and request.method == "PATCH":
            data.pop("comments_count", None)
        return data

    def validate(self, attrs):
        """
        Validate task data.

        - Ensures user has access to the board (owner or member)
        - Ensures assignee and reviewer are board members
        - Prevents changing task's board after creation

        Args:
            attrs (dict): Attributes to validate

        Returns:
            dict: Validated attributes

        Raises:
            ValidationError: If validation fails
        """
        board = self._get_board(attrs)
        if not self.instance:
            self._validate_board_access(board)
        self._validate_user_role(attrs.get('assignee'), board, 'Assignee')
        self._validate_user_role(attrs.get('reviewer'), board, 'Reviewer')

        self._prevent_board_change(attrs)

        return attrs

    def _validate_board_access(self, board):
        """
        Validate that the current user has access to the board.

        Args:
            board (Board): Board to check access for

        Raises:
            ValidationError: If user is not owner or member of the board
        """
        request = self.context.get('request')
        if not request:
            return

        user = request.user
        if not (board.owner == user or user in board.members.all()):
            raise serializers.ValidationError(
                {"board": "You do not have access to this board. You must be the owner or a member."}
            )

    def _get_board(self, attrs):
        """
        Get the board for this task.

        Args:
            attrs (dict): Validated data attributes

        Returns:
            Board: Board instance

        Raises:
            ValidationError: If board cannot be determined
        """
        board = attrs.get('board')
        if board is not None:
            return board
        instance = getattr(self, 'instance', None)
        if instance is not None:
            return instance.board
        raise serializers.ValidationError(
            {"board": "Board must be provided."}
        )

    def _validate_user_role(self, user, board, role_name):
        """
        Validate that user is a member of the board.

        Args:
            user (User): User to validate (can be None)
            board (Board): Board to check membership
            role_name (str): Role name for error message (e.g., 'Assignee')

        Raises:
            ValidationError: If user is not a board member
        """
        if user is None:
            return

        if not board.members.filter(id=user.id).exists():
            raise serializers.ValidationError(
                {role_name.lower(): f"{role_name} must be Member of Board."}
            )

    def _prevent_board_change(self, attrs):
        """
        Prevent changing a task's board after creation.

        Args:
            attrs (dict): Attributes being updated

        Raises:
            ValidationError: If attempting to change board on existing task
        """
        instance = getattr(self, 'instance', None)
        if instance is None:
            return

        if 'board' in attrs and attrs['board'] != instance.board:
            raise serializers.ValidationError(
                {"board": "Changing the board of a task is not allowed."}
            )


class TaskCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for task comments.

    Handles creation and display of task comments with automatic
    author and timestamp tracking.

    Fields:
        id (int): Comment unique identifier
        author (str): Comment author's full name (read-only)
        content (str): Comment text content
        created_at (datetime): Comment creation timestamp (auto-generated)
    """

    author = serializers.CharField(
        source='author.userprofile.full_name',
        read_only=True,
        help_text="Comment author's full name"
    )
    content = serializers.CharField(
        help_text="Comment text content"
    )

    class Meta:
        model = TaskComment
        fields = ['id', 'author', 'content', 'created_at']

    def validate(self, value):
        """
        Validate comment content is not empty.

        Args:
            value (dict): Comment data to validate

        Returns:
            dict: Validated comment data

        Raises:
            ValidationError: If content is empty or only whitespace
        """
        if not value.get('content').strip():
            raise serializers.ValidationError(
                {"content": "Content cannot be empty."}
            )
        return value
