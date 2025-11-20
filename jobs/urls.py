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
)

router = DefaultRouter()
router.register('companies', CompanyViewSet, basename='company')
router.register('jobs', JobViewSet, basename='job')
router.register('applications', JobApplicationViewSet, basename='application')
router.register('collections', JobCollectionViewSet, basename='collection')

urlpatterns = [
    path('', include(router.urls)),
]
