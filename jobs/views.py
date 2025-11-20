"""
职位API视图
"""

from django.db.models import Q
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Company, Job, JobApplication, JobCollection
from .serializers import (
    CompanySerializer,
    JobListSerializer,
    JobDetailSerializer,
    JobApplicationSerializer,
    JobCollectionSerializer,
)


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """公司视图集"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'industry']
    ordering_fields = ['name', 'created_at']


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """职位视图集"""
    queryset = Job.objects.filter(is_active=True).select_related('company')
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'company__name', 'description']
    ordering_fields = ['salary_min', 'salary_max', 'created_at', 'publish_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return JobDetailSerializer
        return JobListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # 城市过滤
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city=city)

        # 学历过滤
        education = self.request.query_params.get('education')
        if education:
            queryset = queryset.filter(education=education)

        # 经验过滤
        experience = self.request.query_params.get('experience')
        if experience:
            queryset = queryset.filter(experience=experience)

        # 行业过滤
        industry = self.request.query_params.get('industry')
        if industry:
            queryset = queryset.filter(company__industry__icontains=industry)

        # 薪资范围过滤
        salary_min = self.request.query_params.get('salary_min')
        salary_max = self.request.query_params.get('salary_max')
        if salary_min:
            queryset = queryset.filter(salary_max__gte=int(salary_min))
        if salary_max:
            queryset = queryset.filter(salary_min__lte=int(salary_max))

        # 技能过滤
        skills = self.request.query_params.get('skills')
        if skills:
            skill_list = [s.strip() for s in skills.split(',')]
            for skill in skill_list:
                queryset = queryset.filter(tags__icontains=skill)

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def apply(self, request, pk=None):
        """申请职位"""
        job = self.get_object()

        # 检查是否已申请
        if JobApplication.objects.filter(user=request.user, job=job).exists():
            return Response(
                {'error': '您已经申请过该职位'},
                status=status.HTTP_400_BAD_REQUEST
            )

        application = JobApplication.objects.create(
            user=request.user,
            job=job,
            cover_letter=request.data.get('cover_letter', '')
        )

        serializer = JobApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def collect(self, request, pk=None):
        """收藏/取消收藏职位"""
        job = self.get_object()

        if request.method == 'POST':
            collection, created = JobCollection.objects.get_or_create(
                user=request.user,
                job=job
            )
            if created:
                return Response({'message': '收藏成功'}, status=status.HTTP_201_CREATED)
            return Response({'message': '已收藏'})

        elif request.method == 'DELETE':
            deleted, _ = JobCollection.objects.filter(
                user=request.user,
                job=job
            ).delete()
            if deleted:
                return Response({'message': '取消收藏成功'})
            return Response({'message': '未收藏'})


class JobApplicationViewSet(viewsets.ModelViewSet):
    """职位申请视图集"""
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user).select_related('job__company')


class JobCollectionViewSet(viewsets.ModelViewSet):
    """职位收藏视图集"""
    serializer_class = JobCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobCollection.objects.filter(user=self.request.user).select_related('job__company')

    def create(self, request, *args, **kwargs):
        """收藏职位"""
        job_id = request.data.get('job')
        if not job_id:
            return Response({'error': '请提供职位ID'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({'error': '职位不存在'}, status=status.HTTP_404_NOT_FOUND)

        collection, created = JobCollection.objects.get_or_create(
            user=request.user,
            job=job
        )

        serializer = self.get_serializer(collection)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
