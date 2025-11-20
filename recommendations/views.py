"""
推荐系统API视图
"""

import logging
from pathlib import Path

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RecommendationHistory, SalaryPredictionHistory
from .serializers import (
    JobRecommendationSerializer,
    JobRecommendationResultSerializer,
    SalaryPredictionInputSerializer,
    SalaryPredictionResultSerializer,
    RecommendationHistorySerializer,
    SalaryPredictionHistorySerializer,
)

logger = logging.getLogger(__name__)

# 全局ML模型实例
_recommender = None
_predictor = None


def get_recommender():
    """获取推荐器实例（单例）"""
    global _recommender
    if _recommender is None:
        try:
            from ml_models.recommender import JobRecommender
            _recommender = JobRecommender(model_dir=str(settings.ML_MODELS_DIR))
            model_file = settings.ML_MODELS_DIR / 'job_recommender.pkl'
            if model_file.exists():
                _recommender.load_model(str(model_file))
                logger.info("职位推荐模型加载成功")
            else:
                logger.warning(f"推荐模型文件不存在: {model_file}")
        except Exception as e:
            logger.error(f"加载推荐模型失败: {e}")
    return _recommender


def get_predictor():
    """获取预测器实例（单例）"""
    global _predictor
    if _predictor is None:
        try:
            from ml_models.predictor import SalaryPredictor
            _predictor = SalaryPredictor(model_dir=str(settings.ML_MODELS_DIR))
            model_file = settings.ML_MODELS_DIR / 'salary_predictor.pkl'
            if model_file.exists():
                _predictor.load_model(str(model_file))
                logger.info("薪资预测模型加载成功")
            else:
                logger.warning(f"预测模型文件不存在: {model_file}")
        except Exception as e:
            logger.error(f"加载预测模型失败: {e}")
    return _predictor


class JobRecommendationView(APIView):
    """职位推荐API"""
    permission_classes = [AllowAny]

    def post(self, request):
        """
        基于用户画像推荐职位

        请求体:
        {
            "skills": ["Python", "Django"],
            "experience": "3-5年",
            "education": "本科",
            "preferred_city": "北京",
            "preferred_industry": "互联网",
            "top_n": 10
        }
        """
        serializer = JobRecommendationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        recommender = get_recommender()

        if recommender is None or recommender.tfidf_matrix is None:
            return Response(
                {'error': '推荐模型未就绪，请稍后重试'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # 构建用户画像
            user_profile = {
                'skills': data.get('skills', []),
                'experience': data.get('experience', '不限'),
                'education': data.get('education', '不限'),
                'preferred_city': data.get('preferred_city', ''),
                'preferred_industry': data.get('preferred_industry', ''),
            }

            # 获取推荐
            top_n = data.get('top_n', 10)
            recommendations = recommender.recommend_by_profile(user_profile, top_n=top_n)

            # 格式化结果
            results = []
            for rec in recommendations:
                results.append({
                    'job_id': rec.get('job_id', 0),
                    'job_title': rec.get('job_title', ''),
                    'company_name': rec.get('company_name', ''),
                    'city': rec.get('city', ''),
                    'salary_min': rec.get('salary_min', 0),
                    'salary_max': rec.get('salary_max', 0),
                    'education': rec.get('education', ''),
                    'experience': rec.get('experience', ''),
                    'similarity_score': round(rec.get('similarity_score', 0), 3),
                    'tags': rec.get('job_tags', '').split(',') if rec.get('job_tags') else [],
                })

            # 记录推荐历史（如果用户已登录）
            if request.user.is_authenticated:
                for rec in results[:5]:  # 只记录前5个
                    RecommendationHistory.objects.create(
                        user=request.user,
                        job_id=rec['job_id'],
                        similarity_score=rec['similarity_score']
                    )

            return Response({
                'count': len(results),
                'recommendations': results
            })

        except Exception as e:
            logger.error(f"推荐失败: {e}")
            return Response(
                {'error': f'推荐失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SalaryPredictionView(APIView):
    """薪资预测API"""
    permission_classes = [AllowAny]

    def post(self, request):
        """
        预测职位薪资

        请求体:
        {
            "city": "北京",
            "education": "本科",
            "experience": "3-5年",
            "industry": "互联网",
            "company_size": "100-499人",
            "company_type": "民营",
            "salary_months": 13,
            "skills": ["Python", "Django", "MySQL"]
        }
        """
        serializer = SalaryPredictionInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        predictor = get_predictor()

        if predictor is None or predictor.model is None:
            return Response(
                {'error': '预测模型未就绪，请稍后重试'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # 构建特征
            job_features = {
                'city': data['city'],
                'education': data['education'],
                'experience': data['experience'],
                'industry': data.get('industry', '互联网'),
                'company_size': data.get('company_size', '100-499人'),
                'company_type': data.get('company_type', '民营'),
                'salary_months': data.get('salary_months', 12),
                'skills': data.get('skills', []),
            }

            # 预测
            avg_salary = predictor.predict(job_features)
            avg, min_sal, max_sal = predictor.predict_salary_range(job_features, confidence=0.8)

            # 计算年薪
            annual_salary = avg * job_features['salary_months']

            result = {
                'predicted_salary': round(avg_salary, 0),
                'salary_min': round(min_sal, 0),
                'salary_max': round(max_sal, 0),
                'annual_salary': round(annual_salary / 10000, 1),  # 万元
                'confidence': 0.8
            }

            # 记录预测历史
            if request.user.is_authenticated:
                SalaryPredictionHistory.objects.create(
                    user=request.user,
                    city=data['city'],
                    education=data['education'],
                    experience=data['experience'],
                    industry=data.get('industry', ''),
                    skills=data.get('skills', []),
                    predicted_salary=avg_salary,
                    salary_min=min_sal,
                    salary_max=max_sal
                )
            else:
                # 匿名用户也记录
                SalaryPredictionHistory.objects.create(
                    city=data['city'],
                    education=data['education'],
                    experience=data['experience'],
                    industry=data.get('industry', ''),
                    skills=data.get('skills', []),
                    predicted_salary=avg_salary,
                    salary_min=min_sal,
                    salary_max=max_sal
                )

            return Response(result)

        except Exception as e:
            logger.error(f"预测失败: {e}")
            return Response(
                {'error': f'预测失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RecommendationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """推荐历史视图集"""
    serializer_class = RecommendationHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RecommendationHistory.objects.filter(user=self.request.user)


class SalaryPredictionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """薪资预测历史视图集"""
    serializer_class = SalaryPredictionHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SalaryPredictionHistory.objects.filter(user=self.request.user)


class ModelStatusView(APIView):
    """模型状态API"""
    permission_classes = [AllowAny]

    def get(self, request):
        """获取ML模型状态"""
        recommender = get_recommender()
        predictor = get_predictor()

        return Response({
            'recommender': {
                'loaded': recommender is not None and recommender.tfidf_matrix is not None,
                'jobs_count': len(recommender.df) if recommender and recommender.df is not None else 0,
                'features_count': len(recommender.feature_names) if recommender else 0,
            },
            'predictor': {
                'loaded': predictor is not None and predictor.model is not None,
                'features_count': len(predictor.feature_columns) if predictor else 0,
            }
        })
