"""
Board API serializers.

This module contains serializers for board management including creation,
listing, updating, and detailed board views.
"""

from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import Board
from tasks_app.api.serializers import TaskSerializer
from tasks_app.models import Task


class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for board list view.
    
    Provides summary information for boards including member count,
    task counts, and statistics for quick overview.
    
    Fields:
        id (int): Board unique identifier
        title (str): Board name
        member_count (int): Number of board members
        ticket_count (int): Total number of tasks on board
        tasks_to_do_count (int): Number of tasks in 'to-do' status
        tasks_high_prio_count (int): Number of high priority tasks
        owner_id (int): Board owner's user ID
    """
    
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = Board
        fields = ['id', 'title', 'member_count', 'ticket_count',
                  'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']

    def get_member_count(self, obj):
        """Return the number of board members."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the total number of tasks on this board."""
        return Task.objects.filter(board=obj).count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks in 'to-do' status."""
        return Task.objects.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of high priority tasks on this board."""
        return Task.objects.filter(board=obj, priority='high').count()


class BoardCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for board creation.
    
    Creates a new board with the requesting user as owner and assigns
    specified users as members.
    
    Fields:
        title (str): Board name
        members (list): List of user IDs to add as board members
    """
    
    members = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True,
        help_text="List of user IDs to add as members"
    )

    class Meta:
        model = Board
        fields = ['title', 'members']

    def create(self, validated_data):
        """
        Create a new board with owner and members.
        
        Args:
            validated_data (dict): Validated board data
            
        Returns:
            Board: Newly created board instance
        """
        members = validated_data.pop('members', [])
        owner = self.context['request'].user
        
        # Create board with current user as owner
        board = Board.objects.create(owner=owner, **validated_data)
        
        # Add specified users as members
        users = User.objects.filter(id__in=members)
        board.members.set(users)
        
        return board


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user information.
    
    Provides basic user details including full name from UserProfile.
    
    Fields:
        id (int): User unique identifier
        fullname (str): User's full display name from profile
        email (str): User's email address
    """
    
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'fullname', 'email']

    def get_fullname(self, obj):
        """Retrieve full name from associated UserProfile."""
        return obj.userprofile.full_name


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed board view.
    
    Provides complete board information including owner details,
    member list, and all associated tasks.
    
    Fields:
        id (int): Board unique identifier
        title (str): Board name
        owner_id (int): Board owner's user ID
        members (list): List of board members with full details
        tasks (list): All tasks associated with this board
    """
    
    owner_id = serializers.ReadOnlyField(source='owner.id')
    members = UserSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_tasks(self, obj):
        """Retrieve all tasks for this board with full details."""
        tasks = Task.objects.filter(board=obj)
        return TaskSerializer(tasks, many=True).data


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for board updates.
    
    Allows updating board title and/or member list. Both fields are optional
    to support partial updates (PATCH).
    
    Fields:
        title (str): Board name (optional)
        members (list): List of user IDs to set as members (optional)
    """
    
    members = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False,
        help_text="List of user IDs to set as board members"
    )
    title = serializers.CharField(
        required=False,
        help_text="Board title/name"
    )

    class Meta:
        model = Board
        fields = ['title', 'members']

    def validate_members(self, value):
        """
        Validate that all provided user IDs exist.
        
        Args:
            value (list): List of user IDs
            
        Returns:
            list: Validated user IDs
            
        Raises:
            ValidationError: If any user ID doesn't exist
        """
        members = User.objects.filter(id__in=value)
        ids = set(value) - set(members.values_list('id', flat=True))

        if ids:
            raise serializers.ValidationError(
                f"Users with IDs {', '.join(map(str, ids))} do not exist."
            )
        return value

    def update(self, instance, validated_data):
        """
        Update board title and/or members.
        
        Args:
            instance (Board): Board instance to update
            validated_data (dict): Validated update data
            
        Returns:
            Board: Updated board instance
        """
        members = validated_data.pop('members', None)
        title = validated_data.get('title', None)

        # Update title if provided
        if title is not None:
            instance.title = title

        # Update members if provided
        if members is not None:
            users = User.objects.filter(id__in=members)
            instance.members.set(users)

        instance.save()
        return instance


class BoardUpdatedSerializer(serializers.ModelSerializer):
    """
    Serializer for board update response.
    
    Returns updated board data with full owner and member details
    after a successful update operation.
    
    Fields:
        id (int): Board unique identifier
        title (str): Board name
        owner_data (dict): Complete owner information
        members_data (list): Complete member information
    """
    
    owner_data = UserSerializer(source="owner", read_only=True)
    members_data = UserSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']
