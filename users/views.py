"""
用户API视图
"""

from django.contrib.auth import authenticate, get_user_model
from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile, UserAccessLog, AICallLog
from .permissions import IsAdminUser
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    LoginSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    """用户注册"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """用户登录"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            })
        return Response(
            {'error': '用户名或密码错误'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """用户登出"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 删除token
        Token.objects.filter(user=request.user).delete()
        return Response({'message': '登出成功'})


class UserProfileView(APIView):
    """用户信息"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取当前用户信息"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """更新用户信息"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """部分更新用户信息"""
        return self.put(request)


class UserProfileDetailView(APIView):
    """用户档案详情"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取用户档案"""
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        """更新用户档案"""
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """修改密码"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            # 删除旧token，要求重新登录
            Token.objects.filter(user=request.user).delete()
            return Response({'message': '密码修改成功，请重新登录'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 管理员API接口
class AdminUserManagementView(APIView):
    """管理员 - 用户管理"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        """获取所有用户列表"""
        users = User.objects.all().order_by('-created_at')

        # 支持搜索
        search = request.query_params.get('search', '')
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )

        # 支持角色筛选
        role = request.query_params.get('role', '')
        if role:
            users = users.filter(role=role)

        # 分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size

        total = users.count()
        users_data = UserSerializer(users[start:end], many=True).data

        return Response({
            'users': users_data,
            'total': total,
            'page': page,
            'page_size': page_size
        })

    def delete(self, request):
        """删除用户"""
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': '缺少user_id参数'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            if user.role == 'admin':
                return Response({'error': '不能删除管理员用户'}, status=status.HTTP_403_FORBIDDEN)
            user.delete()
            return Response({'message': '用户删除成功'})
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)


class AdminUserDetailView(APIView):
    """管理员 - 用户详情"""
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        """获取用户详情"""
        try:
            user = User.objects.get(id=user_id)
            return Response(UserSerializer(user).data)
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id):
        """更新用户信息"""
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_statistics_view(request):
    """管理员 - 统计数据"""
    from jobs.models import Job, Company, JobApplication

    # 用户统计
    total_users = User.objects.count()
    user_count = User.objects.filter(role='user').count()
    admin_count = User.objects.filter(role='admin').count()

    # 职位统计
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()

    # 公司统计
    total_companies = Company.objects.count()

    # 申请统计
    total_applications = JobApplication.objects.count()

    # 最近注册用户
    recent_users = User.objects.order_by('-created_at')[:10]

    return Response({
        'users': {
            'total': total_users,
            'normal_users': user_count,
            'admins': admin_count,
        },
        'jobs': {
            'total': total_jobs,
            'active': active_jobs,
        },
        'companies': {
            'total': total_companies,
        },
        'applications': {
            'total': total_applications,
        },
        'recent_users': UserSerializer(recent_users, many=True).data
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_analytics_view(request):
    """管理员 - 图表分析数据"""
    from datetime import datetime, timedelta
    from django.db.models import Count, Sum
    from django.db.models.functions import TruncDate

    # 获取日期范围参数，默认最近30天
    days = int(request.GET.get('days', 30))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # 1. 用户访问趋势（按天统计）
    access_trend = UserAccessLog.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    access_data = [
        {
            'date': item['date'].strftime('%Y-%m-%d'),
            'count': item['count']
        }
        for item in access_trend
    ]

    # 2. AI调用趋势（按天统计）
    ai_call_trend = AICallLog.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    ai_call_data = [
        {
            'date': item['date'].strftime('%Y-%m-%d'),
            'count': item['count']
        }
        for item in ai_call_trend
    ]

    # 3. AI调用类型分布
    ai_call_by_type = AICallLog.objects.filter(
        created_at__gte=start_date
    ).values('call_type').annotate(
        count=Count('id')
    ).order_by('-count')

    ai_type_data = [
        {
            'type': item['call_type'],
            'name': dict(AICallLog.CALL_TYPE_CHOICES).get(item['call_type'], item['call_type']),
            'count': item['count']
        }
        for item in ai_call_by_type
    ]

    # 4. Token使用统计
    token_stats = AICallLog.objects.filter(
        created_at__gte=start_date
    ).aggregate(
        total_prompt_tokens=Sum('prompt_tokens'),
        total_completion_tokens=Sum('completion_tokens'),
        total_tokens=Sum('total_tokens'),
        total_calls=Count('id'),
        success_calls=Count('id', filter=Q(success=True))
    )

    # 5. 用户注册趋势
    user_register_trend = User.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    register_data = [
        {
            'date': item['date'].strftime('%Y-%m-%d'),
            'count': item['count']
        }
        for item in user_register_trend
    ]

    # 6. 最活跃用户（访问次数最多）
    top_active_users = UserAccessLog.objects.filter(
        created_at__gte=start_date,
        user__isnull=False
    ).values('user__username', 'user__id').annotate(
        access_count=Count('id')
    ).order_by('-access_count')[:10]

    active_users_data = [
        {
            'username': item['user__username'],
            'user_id': item['user__id'],
            'access_count': item['access_count']
        }
        for item in top_active_users
    ]

    # 7. AI调用最多的用户
    top_ai_users = AICallLog.objects.filter(
        created_at__gte=start_date,
        user__isnull=False
    ).values('user__username', 'user__id').annotate(
        call_count=Count('id'),
        total_tokens=Sum('total_tokens')
    ).order_by('-call_count')[:10]

    ai_users_data = [
        {
            'username': item['user__username'],
            'user_id': item['user__id'],
            'call_count': item['call_count'],
            'total_tokens': item['total_tokens'] or 0
        }
        for item in top_ai_users
    ]

    # 8. 平均响应时间趋势
    response_time_trend = AICallLog.objects.filter(
        created_at__gte=start_date,
        response_time__isnull=False
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        avg_time=Sum('response_time') / Count('id')
    ).order_by('date')

    response_time_data = [
        {
            'date': item['date'].strftime('%Y-%m-%d'),
            'avg_time': round(float(item['avg_time']), 2)
        }
        for item in response_time_trend
    ]

    return Response({
        'access_trend': access_data,
        'ai_call_trend': ai_call_data,
        'ai_type_distribution': ai_type_data,
        'token_stats': token_stats,
        'user_register_trend': register_data,
        'top_active_users': active_users_data,
        'top_ai_users': ai_users_data,
        'response_time_trend': response_time_data,
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'days': days
        }
    })
