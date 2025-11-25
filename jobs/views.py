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
from .pagination import CustomPageNumberPagination


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
    pagination_class = CustomPageNumberPagination
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

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def similar(self, request, pk=None):
        """获取相似职位"""
        job = self.get_object()
        top_n = int(request.query_params.get('top_n', 3))

        try:
            # 导入推荐器
            from recommendations.views import get_recommender

            recommender = get_recommender()
            if recommender is None or recommender.tfidf_matrix is None:
                # 如果模型未加载，返回基于同公司或同技能的简单推荐
                similar_jobs = Job.objects.filter(
                    is_active=True
                ).exclude(id=job.id).select_related('company')[:top_n]

                serializer = JobListSerializer(similar_jobs, many=True)
                return Response({
                    'count': len(serializer.data),
                    'results': serializer.data,
                    'method': 'simple'
                })

            # 使用ML模型推荐相似职位
            try:
                # 注意：recommender使用DataFrame的index作为job_id
                # 需要从DataFrame中查找对应的记录
                if int(pk) in recommender.df.index:
                    recommendations = recommender.recommend_by_job_id(
                        int(pk),
                        top_n=top_n,
                        return_scores=True
                    )

                    # 获取推荐的职位详情
                    job_ids = [rec['job_id'] for rec in recommendations]
                    similar_jobs = Job.objects.filter(
                        id__in=job_ids,
                        is_active=True
                    ).select_related('company')

                    # 创建ID到职位的映射
                    job_map = {job.id: job for job in similar_jobs}

                    # 按推荐顺序组织结果
                    results = []
                    for rec in recommendations:
                        job_obj = job_map.get(rec['job_id'])
                        if job_obj:
                            job_data = JobListSerializer(job_obj).data
                            job_data['similarity_score'] = round(rec['similarity_score'], 3)
                            results.append(job_data)

                    return Response({
                        'count': len(results),
                        'results': results,
                        'method': 'ml'
                    })
                else:
                    # 如果当前职位不在训练数据中，使用简单推荐
                    similar_jobs = Job.objects.filter(
                        is_active=True,
                        company=job.company
                    ).exclude(id=job.id).select_related('company')[:top_n]

                    if similar_jobs.count() < top_n:
                        # 如果同公司职位不够，补充同行业的职位
                        remaining = top_n - similar_jobs.count()
                        additional_jobs = Job.objects.filter(
                            is_active=True,
                            company__industry=job.company.industry
                        ).exclude(
                            id__in=[j.id for j in similar_jobs]
                        ).exclude(id=job.id).select_related('company')[:remaining]

                        similar_jobs = list(similar_jobs) + list(additional_jobs)

                    serializer = JobListSerializer(similar_jobs, many=True)
                    return Response({
                        'count': len(serializer.data),
                        'results': serializer.data,
                        'method': 'simple'
                    })

            except Exception as e:
                # ML推荐失败，使用简单推荐
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"ML推荐失败: {e}")

                similar_jobs = Job.objects.filter(
                    is_active=True
                ).exclude(id=job.id).select_related('company')[:top_n]

                serializer = JobListSerializer(similar_jobs, many=True)
                return Response({
                    'count': len(serializer.data),
                    'results': serializer.data,
                    'method': 'fallback'
                })

        except Exception as e:
            return Response(
                {'error': f'获取相似职位失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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


# 大屏展示数据API
from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_screen_data(request):
    """
    获取数据大屏展示所需的数据
    """
    from django.db.models import Count, Avg, Sum

    # 1. 城市职位分布（地图数据）
    city_distribution = Job.objects.filter(is_active=True).values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:20]

    city_data = [
        {'name': item['city'], 'value': item['count']}
        for item in city_distribution if item['city']
    ]

    # 2. 行业分布（玫瑰图数据）
    industry_distribution = Company.objects.values('industry').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    industry_data = [
        {'name': item['industry'] or '未知', 'value': item['count']}
        for item in industry_distribution
    ]

    # 3. 薪资区间分布（柱状图数据）
    jobs_with_salary = Job.objects.filter(
        is_active=True,
        salary_min__isnull=False,
        salary_max__isnull=False
    )

    salary_ranges = [
        {'name': '0-5k', 'min': 0, 'max': 5000},
        {'name': '5-10k', 'min': 5000, 'max': 10000},
        {'name': '10-15k', 'min': 10000, 'max': 15000},
        {'name': '15-20k', 'min': 15000, 'max': 20000},
        {'name': '20-30k', 'min': 20000, 'max': 30000},
        {'name': '30-50k', 'min': 30000, 'max': 50000},
        {'name': '50k+', 'min': 50000, 'max': 999999},
    ]

    salary_data = []
    for range_item in salary_ranges:
        # 使用薪资中位数来判断职位属于哪个区间
        # 中位数 = (salary_min + salary_max) / 2
        if range_item['name'] == '50k+':
            # 对于50k+，只要最小薪资>=50k即可
            count = jobs_with_salary.filter(
                salary_min__gte=range_item['min']
            ).count()
        else:
            # 计算中位数，判断是否在区间内
            from django.db.models import F, ExpressionWrapper, FloatField

            count = jobs_with_salary.annotate(
                avg_salary=ExpressionWrapper(
                    (F('salary_min') + F('salary_max')) / 2.0,
                    output_field=FloatField()
                )
            ).filter(
                avg_salary__gte=range_item['min'],
                avg_salary__lt=range_item['max']
            ).count()

        salary_data.append({
            'name': range_item['name'],
            'value': count
        })

    # 4. TOP公司招聘排行（按职位数量）
    top_companies = Company.objects.annotate(
        job_count=Count('jobs', filter=Q(jobs__is_active=True))
    ).order_by('-job_count')[:10]

    company_ranking = [
        {
            'name': company.name,
            'value': company.job_count,
            'industry': company.industry or '未知'
        }
        for company in top_companies if company.job_count > 0
    ]

    # 5. 热门技能TOP10
    all_tags = []
    jobs_with_tags = Job.objects.filter(is_active=True, tags__isnull=False)
    for job in jobs_with_tags:
        if isinstance(job.tags, list):
            all_tags.extend(job.tags)
        elif isinstance(job.tags, str):
            try:
                import json
                tags = json.loads(job.tags)
                if isinstance(tags, list):
                    all_tags.extend(tags)
            except:
                pass

    tag_counter = Counter(all_tags)
    top_skills = [
        {'name': tag, 'value': count}
        for tag, count in tag_counter.most_common(10)
    ]

    # 6. 实时统计数据
    total_stats = {
        'total_jobs': Job.objects.filter(is_active=True).count(),
        'total_companies': Company.objects.count(),
        'total_applications': JobApplication.objects.count(),
        'avg_salary': Job.objects.filter(
            is_active=True,
            salary_min__isnull=False,
            salary_max__isnull=False
        ).aggregate(
            avg=(Avg('salary_min') + Avg('salary_max')) / 2
        )['avg'] or 0,
    }

    # 7. 学历要求分布
    education_distribution = Job.objects.filter(is_active=True).values('education').annotate(
        count=Count('id')
    ).order_by('-count')

    education_data = [
        {'name': item['education'] or '不限', 'value': item['count']}
        for item in education_distribution
    ]

    # 8. 工作经验要求分布
    experience_distribution = Job.objects.filter(is_active=True).values('experience').annotate(
        count=Count('id')
    ).order_by('-count')

    experience_data = [
        {'name': item['experience'] or '不限', 'value': item['count']}
        for item in experience_distribution
    ]

    return Response({
        'city_distribution': city_data,
        'industry_distribution': industry_data,
        'salary_distribution': salary_data,
        'top_companies': company_ranking,
        'top_skills': top_skills,
        'statistics': total_stats,
        'education_distribution': education_data,
        'experience_distribution': experience_data,
    })


# 简历优化和文档导出 API
from django.http import HttpResponse
from .document_generator import ReportGenerator, ResumeDocumentGenerator


@api_view(['POST'])
@permission_classes([AllowAny])
def optimize_resume(request):
    """
    优化简历内容

    请求参数:
    - resume_text: 原始简历文本
    - analysis_data: 简历分析数据
    - target_position: 目标职位（可选）
    - optimization_goals: 优化目标列表（可选）

    返回:
    - success: 是否成功
    - optimized_resume: 优化后的简历数据
    - changes: 修改说明列表
    - optimization_summary: 整体优化说明
    """
    try:
        resume_text = request.data.get('resume_text')
        analysis_data = request.data.get('analysis_data')
        target_position = request.data.get('target_position')
        optimization_goals = request.data.get('optimization_goals')

        if not resume_text or not analysis_data:
            return Response(
                {'error': '缺少必要参数：resume_text 和 analysis_data'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建优化器
        from .ai_analyzer import ResumeOptimizer
        optimizer = ResumeOptimizer()

        # 执行优化
        result = optimizer.optimize_resume(
            resume_text=resume_text,
            analysis_data=analysis_data,
            target_position=target_position,
            optimization_goals=optimization_goals
        )

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'优化简历时出错: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def get_improvement_suggestions(request):
    """
    获取简历改进建议

    请求参数:
    - analysis_data: 简历分析数据
    - target_position: 目标职位（可选）

    返回:
    - suggestions: 改进建议列表
    """
    try:
        analysis_data = request.data.get('analysis_data')
        target_position = request.data.get('target_position')

        if not analysis_data:
            return Response(
                {'error': '缺少必要参数：analysis_data'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建优化器
        from .ai_analyzer import ResumeOptimizer
        optimizer = ResumeOptimizer()

        # 生成建议
        suggestions = optimizer.generate_improvement_suggestions(
            analysis_data=analysis_data,
            target_position=target_position
        )

        return Response({
            'success': True,
            'suggestions': suggestions
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'生成建议时出错: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def export_analysis_report(request):
    """
    导出分析报告（Word 格式）

    请求参数:
    - analysis_data: 简历分析数据
    - recommendations: AI 推荐内容（可选）
    - chat_history: 对话历史（可选）
    - format: 文档格式（word，未来可扩展 pdf）

    返回:
    - Word 文档文件下载流
    """
    try:
        analysis_data = request.data.get('analysis_data')
        recommendations = request.data.get('recommendations', '')
        chat_history = request.data.get('chat_history', [])
        file_format = request.data.get('format', 'word')

        if not analysis_data:
            return Response(
                {'error': '缺少必要参数：analysis_data'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建报告生成器
        generator = ReportGenerator()

        if file_format == 'word':
            # 生成 Word 报告
            buffer = generator.generate_analysis_report_word(
                analysis_data=analysis_data,
                recommendations=recommendations,
                chat_history=chat_history
            )

            # 准备响应
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = 'attachment; filename="简历分析报告.docx"'
            return response
        else:
            return Response(
                {'error': f'不支持的格式: {file_format}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {'error': f'导出报告时出错: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def export_resume_document(request):
    """
    导出优化后的简历文档（Word 格式）

    请求参数:
    - resume_data: 简历数据（结构化或分析数据）
    - template_style: 模板风格（modern/classic，可选）
    - format: 文档格式（word，未来可扩展 pdf）
    - optimized_content: AI 优化后的文本（可选）

    返回:
    - Word 文档文件下载流
    """
    try:
        resume_data = request.data.get('resume_data')
        template_style = request.data.get('template_style', 'modern')
        file_format = request.data.get('format', 'word')
        optimized_content = request.data.get('optimized_content')

        if not resume_data:
            return Response(
                {'error': '缺少必要参数：resume_data'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建简历文档生成器
        generator = ResumeDocumentGenerator()

        if file_format == 'word':
            # 判断是完整简历数据还是分析数据
            if 'personal_info' in resume_data or 'work_experience' in resume_data:
                # 完整简历数据
                buffer = generator.generate_resume_word(
                    resume_data=resume_data,
                    template_style=template_style
                )
            else:
                # 简历分析数据，生成简单格式
                buffer = generator.generate_simple_resume_word(
                    analysis_data=resume_data,
                    optimized_content=optimized_content
                )

            # 准备响应
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = 'attachment; filename="优化后的简历.docx"'
            return response
        else:
            return Response(
                {'error': f'不支持的格式: {file_format}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {'error': f'导出简历时出错: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
