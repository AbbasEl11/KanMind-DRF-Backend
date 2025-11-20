"""
Task API URL configuration.

Defines URL patterns for task management, nested comment endpoints,
and filtered task views. Uses nested routers for hierarchical resources.
"""

from django.urls import path, include
from rest_framework_nested import routers
from .views import TaskViewSet, TaskCommentsViewSet, TaskAssignedOrReviewerViewSet


# Main router for task operations
router = routers.SimpleRouter()
router.register(r'tasks', TaskViewSet, basename='tasks')

# Nested router for task comments
# Creates URLs like /api/tasks/{task_id}/comments/
comments_router = routers.NestedSimpleRouter(router, r'tasks', lookup='task')
comments_router.register(
    r'comments', TaskCommentsViewSet, basename='task-comments')

urlpatterns = [
    # Filtered task views
    # GET /api/tasks/assigned-to-me/ - Tasks assigned to current user
    path('tasks/assigned-to-me/', 
         TaskAssignedOrReviewerViewSet.as_view({'get': 'list'}, mode="assigned"), 
         name='tasks-assigned'),
    
    # GET /api/tasks/reviewing/ - Tasks user is reviewing
    path('tasks/reviewing/', 
         TaskAssignedOrReviewerViewSet.as_view({'get': 'list'}, mode="reviewer"), 
         name='tasks-reviewer'),
    
    # Task CRUD endpoints
    # POST /api/tasks/ - Create task
    # PUT/PATCH /api/tasks/{id}/ - Update task
    # DELETE /api/tasks/{id}/ - Delete task
    path('', include(router.urls)),
    
    # Nested comment endpoints
    # GET /api/tasks/{task_id}/comments/ - List comments
    # POST /api/tasks/{task_id}/comments/ - Create comment
    # DELETE /api/tasks/{task_id}/comments/{id}/ - Delete comment
    path('', include(comments_router.urls)),
]
