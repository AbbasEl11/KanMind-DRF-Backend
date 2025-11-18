from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers

from tasks_app.api.serializers import TaskSerializer
from ..models import Board
from tasks_app.models import Task


class BoardListSerializer(serializers.ModelSerializer):
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
        return obj.members.count()

    def get_ticket_count(self, obj):
        return Task.objects.filter(board=obj).count()

    def get_tasks_to_do_count(self, obj):
        return Task.objects.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return Task.objects.filter(board=obj, priority='high').count()


class BoardCreateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = Board
        fields = ['title', 'members']

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        owner = self.context['request'].user
        board = Board.objects.create(owner=owner, **validated_data)
        users = User.objects.filter(id__in=members)
        board.members.set(users)
        return board


class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'fullname', 'email']

    def get_fullname(self, obj):
        return obj.userprofile.full_name


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.ReadOnlyField(source='owner.id')
    members = UserSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_tasks(self, obj):
        tasks = Task.objects.filter(board=obj)
        return TaskSerializer(tasks, many=True).data


class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False)
    title = serializers.CharField(required=False)

    class Meta:
        model = Board
        fields = ['title', 'members']

    def validate_members(self, value):
        members = User.objects.filter(id__in=value)
        ids = set(value) - set(members.values_list('id', flat=True))

        if ids:
            raise serializers.ValidationError(
                "Ids not found"
            )
        return value

    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        title = validated_data.get('title', None)

        if title is not None:
            instance.title = title

        if members is not None:
            users = User.objects.filter(id__in=members)
            instance.members.set(users)

        instance.save()
        return instance


class BoardUpdatedSerializer(serializers.ModelSerializer):
    owner_data = UserSerializer(source="owner", read_only=True)
    members_data = UserSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data',  'members_data',]
