"""
URL configuration for job_platform project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.views import APIView


class APIRootView(APIView):
    """API根视图"""

    def get(self, request):
        return Response({
            'message': '招聘数据分析与职位推荐系统 API',
            'version': '1.0.0',
            'endpoints': {
                'jobs': '/api/jobs/',
                'users': '/api/users/',
                'recommendations': '/api/ml/',
                'admin': '/admin/',
            }
        })


urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('admin/', admin.site.urls),
    path('api/jobs/', include('jobs.urls')),
    path('api/users/', include('users.urls')),
    path('api/ml/', include('recommendations.urls')),
]
