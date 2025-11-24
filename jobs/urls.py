"""
职位URL配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CompanyViewSet,
    JobViewSet,
    JobApplicationViewSet,
    JobCollectionViewSet,
    ResumeAnalysisViewSet,
    ConversationalAssistantViewSet,
)

router = DefaultRouter()
router.register('companies', CompanyViewSet, basename='company')
router.register('jobs', JobViewSet, basename='job')
router.register('applications', JobApplicationViewSet, basename='application')
router.register('collections', JobCollectionViewSet, basename='collection')
router.register('resume-analysis', ResumeAnalysisViewSet, basename='resume-analysis')
router.register('ai-assistant', ConversationalAssistantViewSet, basename='ai-assistant')

urlpatterns = [
    path('', include(router.urls)),
]
