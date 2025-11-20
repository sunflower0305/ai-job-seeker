"""
职位模型
"""

from django.db import models


class Company(models.Model):
    """公司模型"""

    COMPANY_TYPE_CHOICES = [
        ('民营', '民营'),
        ('国企', '国企'),
        ('外企', '外企'),
        ('上市公司', '上市公司'),
        ('创业公司', '创业公司'),
        ('其他', '其他'),
    ]

    COMPANY_SIZE_CHOICES = [
        ('20人以下', '20人以下'),
        ('20-99人', '20-99人'),
        ('100-499人', '100-499人'),
        ('500-999人', '500-999人'),
        ('1000-9999人', '1000-9999人'),
        ('10000人以上', '10000人以上'),
    ]

    name = models.CharField('公司名称', max_length=200)
    industry = models.CharField('行业', max_length=100, blank=True)
    company_type = models.CharField('公司类型', max_length=50, choices=COMPANY_TYPE_CHOICES, default='其他')
    company_size = models.CharField('公司规模', max_length=50, choices=COMPANY_SIZE_CHOICES, blank=True)
    description = models.TextField('公司简介', blank=True)
    website = models.URLField('公司网站', blank=True)
    logo = models.URLField('公司Logo', blank=True)
    address = models.CharField('公司地址', max_length=500, blank=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '公司'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Job(models.Model):
    """职位模型"""

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

    # 基本信息
    title = models.CharField('职位名称', max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs', verbose_name='公司')
    city = models.CharField('城市', max_length=50)
    district = models.CharField('区域', max_length=100, blank=True)

    # 薪资信息
    salary_min = models.IntegerField('最低薪资', default=0)
    salary_max = models.IntegerField('最高薪资', default=0)
    salary_months = models.IntegerField('薪资月数', default=12)

    # 职位要求
    education = models.CharField('学历要求', max_length=20, choices=EDUCATION_CHOICES, default='不限')
    experience = models.CharField('经验要求', max_length=20, choices=EXPERIENCE_CHOICES, default='不限')

    # 详细信息
    description = models.TextField('职位描述', blank=True)
    requirements = models.TextField('任职要求', blank=True)
    welfare = models.CharField('福利待遇', max_length=500, blank=True)
    tags = models.JSONField('技能标签', default=list, blank=True)

    # 数据来源
    source = models.CharField('数据来源', max_length=50, blank=True)
    source_id = models.CharField('来源ID', max_length=100, blank=True)
    source_url = models.URLField('来源链接', blank=True)

    # 状态
    is_active = models.BooleanField('是否有效', default=True)
    publish_date = models.DateField('发布日期', null=True, blank=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '职位'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.company.name}"

    @property
    def salary_avg(self):
        """平均薪资"""
        return (self.salary_min + self.salary_max) / 2

    def get_features_for_prediction(self):
        """获取用于薪资预测的特征"""
        return {
            'city': self.city,
            'education': self.education,
            'experience': self.experience,
            'industry': self.company.industry,
            'company_size': self.company.company_size,
            'company_type': self.company.company_type,
            'salary_months': self.salary_months,
            'skills': self.tags or [],
        }


class JobApplication(models.Model):
    """职位申请"""

    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('viewed', '已查看'),
        ('interview', '邀请面试'),
        ('rejected', '不合适'),
        ('accepted', '已录用'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    cover_letter = models.TextField('求职信', blank=True)

    created_at = models.DateTimeField('申请时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '职位申请'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'job']

    def __str__(self):
        return f"{self.user.username} 申请 {self.job.title}"


class JobCollection(models.Model):
    """职位收藏"""

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='collections')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='collections')
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        verbose_name = '职位收藏'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'job']

    def __str__(self):
        return f"{self.user.username} 收藏 {self.job.title}"
