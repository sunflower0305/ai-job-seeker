"""
用户模型
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型"""

    ROLE_CHOICES = [
        ('jobseeker', '求职者'),
        ('employer', '招聘者'),
        ('admin', '管理员'),
    ]

    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='jobseeker')
    phone = models.CharField('手机号', max_length=20, blank=True)
    avatar = models.URLField('头像', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """求职者档案"""

    EDUCATION_CHOICES = [
        ('不限', '不限'),
        ('大专', '大专'),
        ('本科', '本科'),
        ('硕士', '硕士'),
        ('博士', '博士'),
    ]

    EXPERIENCE_CHOICES = [
        ('不限', '不限'),
        ('1年以下', '1年以下'),
        ('1-3年', '1-3年'),
        ('3-5年', '3-5年'),
        ('5-10年', '5-10年'),
        ('10年以上', '10年以上'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    real_name = models.CharField('真实姓名', max_length=50, blank=True)
    gender = models.CharField('性别', max_length=10, blank=True)
    birth_date = models.DateField('出生日期', null=True, blank=True)

    # 职业信息
    education = models.CharField('学历', max_length=20, choices=EDUCATION_CHOICES, default='不限')
    experience = models.CharField('工作经验', max_length=20, choices=EXPERIENCE_CHOICES, default='不限')
    skills = models.JSONField('技能标签', default=list, blank=True)
    current_position = models.CharField('当前职位', max_length=100, blank=True)
    current_company = models.CharField('当前公司', max_length=100, blank=True)

    # 求职偏好
    preferred_city = models.CharField('期望城市', max_length=50, blank=True)
    preferred_industry = models.CharField('期望行业', max_length=100, blank=True)
    expected_salary_min = models.IntegerField('期望薪资下限', null=True, blank=True)
    expected_salary_max = models.IntegerField('期望薪资上限', null=True, blank=True)

    # 简历
    resume_url = models.URLField('简历链接', blank=True)
    self_introduction = models.TextField('自我介绍', blank=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户档案'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username}的档案"

    def get_profile_for_recommendation(self):
        """获取用于推荐的用户画像"""
        return {
            'skills': self.skills or [],
            'experience': self.experience,
            'education': self.education,
            'preferred_city': self.preferred_city,
            'preferred_industry': self.preferred_industry,
        }
