"""
推荐系统模型
"""

from django.db import models
from django.conf import settings


class RecommendationHistory(models.Model):
    """推荐历史记录"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendation_history')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='recommendation_history')
    similarity_score = models.FloatField('匹配度')
    is_clicked = models.BooleanField('是否点击', default=False)
    is_applied = models.BooleanField('是否申请', default=False)

    created_at = models.DateTimeField('推荐时间', auto_now_add=True)

    class Meta:
        verbose_name = '推荐历史'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"为 {self.user.username} 推荐 {self.job.title}"


class SalaryPredictionHistory(models.Model):
    """薪资预测历史"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='salary_predictions',
        null=True,
        blank=True
    )

    # 预测输入
    city = models.CharField('城市', max_length=50)
    education = models.CharField('学历', max_length=20)
    experience = models.CharField('经验', max_length=20)
    industry = models.CharField('行业', max_length=100)
    skills = models.JSONField('技能', default=list)

    # 预测输出
    predicted_salary = models.FloatField('预测薪资')
    salary_min = models.FloatField('薪资下限', null=True)
    salary_max = models.FloatField('薪资上限', null=True)

    created_at = models.DateTimeField('预测时间', auto_now_add=True)

    class Meta:
        verbose_name = '薪资预测历史'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.city} {self.experience} - {self.predicted_salary:.0f}元"


class UserBehavior(models.Model):
    """用户行为记录"""

    ACTION_CHOICES = [
        ('view', '查看'),
        ('click', '点击'),
        ('apply', '申请'),
        ('collect', '收藏'),
        ('share', '分享'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='behaviors')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='behaviors')
    action = models.CharField('行为类型', max_length=20, choices=ACTION_CHOICES)
    duration = models.IntegerField('停留时长(秒)', default=0)

    created_at = models.DateTimeField('行为时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户行为'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} {self.get_action_display()} {self.job.title}"
