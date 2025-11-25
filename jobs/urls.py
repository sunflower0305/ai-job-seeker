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
    dashboard_screen_data,
    optimize_resume,
    get_improvement_suggestions,
    export_analysis_report,
    export_resume_document,
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
    path('dashboard-screen/', dashboard_screen_data, name='dashboard-screen'),
    # 简历优化和文档导出
    path('resume-optimize/', optimize_resume, name='optimize-resume'),
    path('resume-suggestions/', get_improvement_suggestions, name='resume-suggestions'),
    path('export-report/', export_analysis_report, name='export-report'),
    path('export-resume/', export_resume_document, name='export-resume'),
]
