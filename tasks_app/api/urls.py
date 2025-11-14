from django.urls import path, include
from .views import TaskViewSet, TaskCommentsViewSet, TaskAssignedOrReviewerViewSet
from rest_framework_nested import routers


router = routers.SimpleRouter()
router.register(r'tasks', TaskViewSet, basename='tasks')

comments_router = routers.NestedSimpleRouter(router, r'tasks', lookup='task')
comments_router.register(
    r'comments', TaskCommentsViewSet, basename='task-comments')

urlpatterns = [
    path('tasks/assigned-to-me/', TaskAssignedOrReviewerViewSet.as_view(
        {'get': 'list'}, mode="assigned"), name='tasks-assigned'),
    path('tasks/reviewing/', TaskAssignedOrReviewerViewSet.as_view(
        {'get': 'list'}, mode="reviewer"), name='tasks-reviewer'),
    path('', include(router.urls)),
    path('', include(comments_router.urls)),
]
