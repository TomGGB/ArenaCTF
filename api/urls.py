"""
URLs de la API REST de ArenaCTF
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, TeamViewSet, CategoryViewSet, ChallengeViewSet,
    SubmissionViewSet, FirstBloodViewSet, CTFConfigViewSet,
    ScoreboardViewSet, StatisticsViewSet, AchievementViewSet
)
from .token_views import TokenViewSet
from .root_view import APIRootView

# Router para los viewsets (sin generar vista raíz automática)
router = DefaultRouter(root_renderers=[])
router.register(r'users', UserViewSet, basename='user')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'challenges', ChallengeViewSet, basename='challenge')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'first-bloods', FirstBloodViewSet, basename='firstblood')
router.register(r'config', CTFConfigViewSet, basename='config')
router.register(r'scoreboard', ScoreboardViewSet, basename='scoreboard')
router.register(r'statistics', StatisticsViewSet, basename='statistics')
router.register(r'achievements', AchievementViewSet, basename='achievement')

app_name = 'api'

urlpatterns = [
    path('v1/', APIRootView.as_view(), name='api-root'),
    path('v1/', include(router.urls)),
    path('v1/tokens/', TokenViewSet.as_view(), name='tokens'),
]
