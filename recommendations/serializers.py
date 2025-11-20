"""
推荐系统序列化器
"""

from rest_framework import serializers
from .models import RecommendationHistory, SalaryPredictionHistory


class JobRecommendationSerializer(serializers.Serializer):
    """职位推荐输入序列化器"""
    skills = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='技能列表'
    )
    experience = serializers.CharField(required=False, help_text='工作经验')
    education = serializers.CharField(required=False, help_text='学历')
    preferred_city = serializers.CharField(required=False, help_text='期望城市')
    preferred_industry = serializers.CharField(required=False, help_text='期望行业')
    top_n = serializers.IntegerField(default=10, min_value=1, max_value=50, help_text='推荐数量')


class JobRecommendationResultSerializer(serializers.Serializer):
    """职位推荐结果序列化器"""
    job_id = serializers.IntegerField()
    job_title = serializers.CharField()
    company_name = serializers.CharField()
    city = serializers.CharField()
    salary_min = serializers.IntegerField()
    salary_max = serializers.IntegerField()
    education = serializers.CharField()
    experience = serializers.CharField()
    similarity_score = serializers.FloatField()
    tags = serializers.ListField(child=serializers.CharField(), required=False)


class SalaryPredictionInputSerializer(serializers.Serializer):
    """薪资预测输入序列化器"""
    city = serializers.CharField(help_text='城市')
    education = serializers.CharField(help_text='学历要求')
    experience = serializers.CharField(help_text='工作经验')
    industry = serializers.CharField(required=False, default='互联网', help_text='行业')
    company_size = serializers.CharField(required=False, default='100-499人', help_text='公司规模')
    company_type = serializers.CharField(required=False, default='民营', help_text='公司类型')
    salary_months = serializers.IntegerField(required=False, default=12, help_text='薪资月数')
    skills = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        help_text='技能列表'
    )


class SalaryPredictionResultSerializer(serializers.Serializer):
    """薪资预测结果序列化器"""
    predicted_salary = serializers.FloatField(help_text='预测平均薪资')
    salary_min = serializers.FloatField(help_text='薪资下限')
    salary_max = serializers.FloatField(help_text='薪资上限')
    annual_salary = serializers.FloatField(help_text='年薪估计')
    confidence = serializers.FloatField(help_text='置信度')


class RecommendationHistorySerializer(serializers.ModelSerializer):
    """推荐历史序列化器"""
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.name', read_only=True)

    class Meta:
        model = RecommendationHistory
        fields = ['id', 'job', 'job_title', 'company_name', 'similarity_score',
                  'is_clicked', 'is_applied', 'created_at']


class SalaryPredictionHistorySerializer(serializers.ModelSerializer):
    """薪资预测历史序列化器"""

    class Meta:
        model = SalaryPredictionHistory
        fields = ['id', 'city', 'education', 'experience', 'industry', 'skills',
                  'predicted_salary', 'salary_min', 'salary_max', 'created_at']
