"""
职位API视图
"""

from django.db.models import Q, Count, Avg, Min, Max
from django.http import HttpResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from collections import Counter

from .models import Company, Job, JobApplication, JobCollection
from .serializers import (
    CompanySerializer,
    JobListSerializer,
    JobDetailSerializer,
    JobApplicationSerializer,
    JobCollectionSerializer,
)
from .wordcloud_generator import generate_colorful_wordcloud
from .ai_analyzer import analyze_and_recommend, create_conversational_session


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

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def statistics(self, request):
        """获取职位统计数据"""
        jobs = Job.objects.filter(is_active=True)

        # 日期筛选
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            jobs = jobs.filter(created_at__gte=start_date)
        if end_date:
            jobs = jobs.filter(created_at__lte=end_date)

        # 基础统计
        total_jobs = jobs.count()
        total_companies = Company.objects.count()

        # 薪资统计
        salary_stats = jobs.aggregate(
            avg_salary=Avg('salary_min'),
            min_salary=Min('salary_min'),
            max_salary=Max('salary_max')
        )

        # 按城市统计
        city_distribution = list(
            jobs.values('city')
            .annotate(count=Count('id'), avg_salary=Avg('salary_min'))
            .order_by('-count')[:10]
        )

        # 按学历统计
        education_distribution = list(
            jobs.values('education')
            .annotate(count=Count('id'), avg_salary=Avg('salary_min'))
            .order_by('-count')
        )

        # 按经验统计
        experience_distribution = list(
            jobs.values('experience')
            .annotate(count=Count('id'), avg_salary=Avg('salary_min'))
            .order_by('-count')
        )

        # 按行业统计（从公司获取）
        industry_distribution = list(
            jobs.values('company__industry')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # 薪资区间分布
        salary_ranges = {
            '0-5k': jobs.filter(salary_max__lt=5000).count(),
            '5-10k': jobs.filter(salary_min__gte=5000, salary_max__lt=10000).count(),
            '10-15k': jobs.filter(salary_min__gte=10000, salary_max__lt=15000).count(),
            '15-20k': jobs.filter(salary_min__gte=15000, salary_max__lt=20000).count(),
            '20k+': jobs.filter(salary_min__gte=20000).count(),
        }

        # 技能需求统计
        skills_counter = Counter()
        for job in jobs:
            if job.tags:
                for skill in job.tags:
                    if skill:  # 排除空字符串
                        skills_counter[skill] += 1

        # 获取Top 20技能
        skills_distribution = [
            {'skill': skill, 'count': count}
            for skill, count in skills_counter.most_common(20)
        ]

        # 公司类型分布
        company_type_distribution = list(
            jobs.values('company__company_type')
            .annotate(count=Count('id'), avg_salary=Avg('salary_min'))
            .order_by('-count')
        )

        # 公司规模分布
        company_size_distribution = list(
            jobs.values('company__company_size')
            .annotate(count=Count('id'), avg_salary=Avg('salary_min'))
            .order_by('-count')
        )

        return Response({
            'basic_stats': {
                'total_jobs': total_jobs,
                'total_companies': total_companies,
            },
            'salary_stats': {
                'average': round(salary_stats['avg_salary'] or 0, 2),
                'min': salary_stats['min_salary'] or 0,
                'max': salary_stats['max_salary'] or 0,
            },
            'salary_ranges': salary_ranges,
            'city_distribution': city_distribution,
            'education_distribution': education_distribution,
            'experience_distribution': experience_distribution,
            'industry_distribution': industry_distribution,
            'skills_distribution': skills_distribution,
            'company_type_distribution': company_type_distribution,
            'company_size_distribution': company_size_distribution,
        })

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def wordcloud(self, request):
        """生成技能词云图片"""
        jobs = Job.objects.filter(is_active=True)

        # 日期筛选
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            jobs = jobs.filter(created_at__gte=start_date)
        if end_date:
            jobs = jobs.filter(created_at__lte=end_date)

        # 技能需求统计
        skills_counter = Counter()
        for job in jobs:
            if job.tags:
                for skill in job.tags:
                    if skill:
                        skills_counter[skill] += 1

        # 获取Top 30技能
        skills_data = [
            {'skill': skill, 'count': count}
            for skill, count in skills_counter.most_common(30)
        ]

        if not skills_data:
            # 如果没有数据，返回默认提示
            return HttpResponse("No skills data available", status=404)

        # 生成词云图片
        width = int(request.query_params.get('width', 900))
        height = int(request.query_params.get('height', 600))

        img_io = generate_colorful_wordcloud(skills_data, width=width, height=height)

        # 返回图片
        return HttpResponse(img_io.getvalue(), content_type='image/png')

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


class ResumeAnalysisViewSet(viewsets.ViewSet):
    """简历分析和职位推荐视图集"""
    permission_classes = [AllowAny]  # 可以根据需要改为 IsAuthenticated

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def analyze(self, request):
        """
        上传简历文档，进行AI分析并推荐职位

        请求参数:
        - file: 简历文件（PDF、Word或TXT格式）

        返回:
        - success: 是否成功
        - resume_analysis: 简历分析结果
        - recommendation: AI推荐的职位和理由
        """
        # 检查是否有文件上传
        if 'file' not in request.FILES:
            return Response(
                {'error': '请上传简历文件'},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = request.FILES['file']
        filename = uploaded_file.name

        # 验证文件类型
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            return Response(
                {'error': f'不支持的文件类型。支持的格式: {", ".join(allowed_extensions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证文件大小（限制为10MB）
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            return Response(
                {'error': '文件大小不能超过10MB'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 读取文件内容
            file_content = uploaded_file.read()

            # 调用AI分析和推荐服务
            result = analyze_and_recommend(file_content, filename)

            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': result.get('error', '分析失败')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            return Response(
                {'error': f'处理文件时出错: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationalAssistantViewSet(viewsets.ViewSet):
    """对话式AI助手视图集"""
    permission_classes = [AllowAny]

    # 存储会话（实际应用中应该使用缓存或数据库）
    sessions = {}

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def chat(self, request):
        """
        对话接口

        请求参数:
        - message: 用户消息
        - session_id: 会话ID（可选，如果没有则创建新会话）
        - resume_context: 简历分析上下文（可选，首次对话时提供）

        返回:
        - success: 是否成功
        - response: AI响应
        - session_id: 会话ID
        - conversation_history: 对话历史
        """
        message = request.data.get('message')
        if not message:
            return Response(
                {'error': '请提供消息内容'},
                status=status.HTTP_400_BAD_REQUEST
            )

        session_id = request.data.get('session_id')
        resume_context = request.data.get('resume_context')

        # 获取或创建会话
        if session_id and session_id in self.sessions:
            assistant = self.sessions[session_id]
        else:
            import uuid
            session_id = str(uuid.uuid4())
            assistant = create_conversational_session()
            self.sessions[session_id] = assistant

        # 处理消息
        try:
            result = assistant.chat(message, resume_context=resume_context)
            result['session_id'] = session_id
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'处理消息时出错: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset(self, request):
        """
        重置会话

        请求参数:
        - session_id: 会话ID

        返回:
        - success: 是否成功
        - message: 提示消息
        """
        session_id = request.data.get('session_id')
        if not session_id:
            return Response(
                {'error': '请提供会话ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if session_id in self.sessions:
            self.sessions[session_id].reset_conversation()
            return Response({
                'success': True,
                'message': '会话已重置'
            })
        else:
            return Response(
                {'error': '会话不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
