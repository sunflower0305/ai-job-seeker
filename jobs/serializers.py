"""
职位序列化器
"""

from rest_framework import serializers
from .models import Company, Job, JobApplication, JobCollection


class CompanySerializer(serializers.ModelSerializer):
    """公司序列化器"""
    jobs_count = serializers.IntegerField(source='jobs.count', read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'name', 'industry', 'company_type', 'company_size',
                  'description', 'website', 'logo', 'address', 'jobs_count']


class JobListSerializer(serializers.ModelSerializer):
    """职位列表序列化器"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_type = serializers.CharField(source='company.company_type', read_only=True)
    industry = serializers.CharField(source='company.industry', read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'company_name', 'company_type', 'industry',
                  'city', 'salary_min', 'salary_max', 'education', 'experience',
                  'tags', 'publish_date', 'created_at']


class JobDetailSerializer(serializers.ModelSerializer):
    """职位详情序列化器"""
    company = CompanySerializer(read_only=True)
    is_collected = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id', 'title', 'company', 'city', 'district',
                  'salary_min', 'salary_max', 'salary_months',
                  'education', 'experience', 'description', 'requirements',
                  'welfare', 'tags', 'source', 'source_url',
                  'publish_date', 'created_at', 'is_collected', 'is_applied']

    def get_is_collected(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.collections.filter(user=request.user).exists()
        return False

    def get_is_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.applications.filter(user=request.user).exists()
        return False


class JobApplicationSerializer(serializers.ModelSerializer):
    """职位申请序列化器"""
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.name', read_only=True)

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'job_title', 'company_name', 'status',
                  'cover_letter', 'created_at', 'updated_at']
        read_only_fields = ['status']


class JobCollectionSerializer(serializers.ModelSerializer):
    """职位收藏序列化器"""
    job = JobListSerializer(read_only=True)

    class Meta:
        model = JobCollection
        fields = ['id', 'job', 'created_at']
