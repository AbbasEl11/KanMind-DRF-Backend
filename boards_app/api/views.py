"""
Board API views.

This module contains view classes for board management including CRUD operations
and utility endpoints like email checking for user lookup.
"""

from django.contrib.auth.models import User
from rest_framework import viewsets, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Board
from .permissions import IsBoardMemberOrOwner
from .serializers import (
    BoardListSerializer, 
    BoardCreateSerializer, 
    BoardDetailSerializer, 
    BoardUpdatedSerializer, 
    BoardUpdateSerializer
)


class BoardViewSet(viewsets.ModelViewSet):
    """
    API endpoint for board management.
    
    Provides CRUD operations for boards with dynamic serializer selection
    based on the action being performed.
    
    Endpoints:
        GET /api/boards/ - List user's boards (owned or member)
        POST /api/boards/ - Create new board
        GET /api/boards/{id}/ - Retrieve board details
        PUT/PATCH /api/boards/{id}/ - Update board
        DELETE /api/boards/{id}/ - Delete board (owner only)
    
    Permissions:
        - IsAuthenticated: User must be logged in
        - IsBoardMemberOrOwner: User must be owner or member for object-level access
    """
    
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]
    lookup_field = 'pk'

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        
        Returns:
            Serializer: Serializer class for current action
        """
        if self.action == 'list':
            return BoardListSerializer
        elif self.action == 'create':
            return BoardCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_queryset(self):
        """
        Return boards where user is owner or member.
        
        Returns:
            QuerySet: Filtered board queryset for current user
        """
        user = self.request.user
        return (Board.objects.filter(owner=user) | 
                Board.objects.filter(members=user)).distinct()

    def create(self, request, *args, **kwargs):
        """
        Create a new board.
        
        Args:
            request: HTTP request with board data
            
        Returns:
            Response: Created board data (201) or validation errors (400)
        """
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        return Response(
            BoardListSerializer(board).data, 
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """
        Update an existing board.
        
        Supports both full (PUT) and partial (PATCH) updates.
        
        Args:
            request: HTTP request with update data
            
        Returns:
            Response: Updated board data (200) or validation errors (400)
        """
        partial = kwargs.get('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=partial, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        return Response(
            BoardUpdatedSerializer(board).data, 
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        """
        Perform partial update (PATCH) on board.
        
        Args:
            request: HTTP request with partial update data
            
        Returns:
            Response: Updated board data
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a board.
        
        Only board owners can delete boards. Members cannot delete.
        
        Args:
            request: HTTP request
            
        Returns:
            Response: Empty response (204) or forbidden error (403)
        """
        board = self.get_object()

        # Only owner can delete board
        if board.owner != request.user:
            return Response(
                {"detail": "Just Owner can Delete."}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailCheck(views.APIView):
    """
    API endpoint for user lookup by email.
    
    GET /api/email-check/?email=user@example.com
    
    Allows authenticated users to search for other users by email address
    to add them as board members.
    
    Permissions:
        - IsAuthenticated: User must be logged in
        
    Query Parameters:
        email (str): Email address to search for
        
    Returns:
        200: User found with id, email, and fullname
        400: Email parameter missing
        404: No user found with given email
    """
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Search for user by email address.
        
        Args:
            request: HTTP request with email query parameter
            
        Returns:
            Response: User data or error message
        """
        email = request.query_params.get('email')

        # Validate email parameter presence
        if not email:
            return Response(
                {"Error": "Email Paramater is missing"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            fullname = user.userprofile.full_name

            return Response({
                "id": user.id,
                "email": user.email,
                "fullname": fullname
            })
        except User.DoesNotExist:
            return Response(
                {"Error": "No Profile with this email found !"}, 
                status=status.HTTP_404_NOT_FOUND
            )
