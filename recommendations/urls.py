"""
推荐系统URL配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    JobRecommendationView,
    SalaryPredictionView,
    RecommendationHistoryViewSet,
    SalaryPredictionHistoryViewSet,
    ModelStatusView,
)

router = DefaultRouter()
router.register('recommendation-history', RecommendationHistoryViewSet, basename='recommendation-history')
router.register('prediction-history', SalaryPredictionHistoryViewSet, basename='prediction-history')

urlpatterns = [
    path('recommend/', JobRecommendationView.as_view(), name='job-recommend'),
    path('predict-salary/', SalaryPredictionView.as_view(), name='predict-salary'),
    path('model-status/', ModelStatusView.as_view(), name='model-status'),
    path('', include(router.urls)),
]
