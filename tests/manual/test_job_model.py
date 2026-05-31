#!/usr/bin/env python
"""
测试 Job 模型字段
"""

from _bootstrap import PROJECT_ROOT
import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job

print("=== 测试 Job 模型字段 ===\n")

# 获取一个职位
try:
    job = Job.objects.filter(is_active=True).first()

    if job:
        print(f"✓ 找到职位: {job.title}\n")

        # 测试所有字段
        fields_to_test = [
            ('id', job.id),
            ('title', job.title),
            ('city', job.city),
            ('salary_min', job.salary_min),
            ('salary_max', job.salary_max),
            ('education', job.education),
            ('experience', job.experience),
            ('description', job.description),
            ('requirements', job.requirements),
            ('welfare', job.welfare),  # 这是正确的字段名
            ('tags', job.tags),
        ]

        print("字段测试结果：")
        print("-" * 50)
        for field_name, field_value in fields_to_test:
            value_preview = str(field_value)[:50] if field_value else 'None'
            print(f"✓ {field_name:15} : {value_preview}")

        print("\n" + "=" * 50)
        print("✓ 所有字段测试通过！")

        # 测试 get_job_details 函数会使用的字段
        print("\n=== 职位详细信息 ===")
        print(f"ID: {job.id}")
        print(f"标题: {job.title}")
        print(f"公司: {job.company.name if job.company else '未知'}")
        print(f"薪资: {job.salary_min}-{job.salary_max}元/月")
        print(f"城市: {job.city}")
        print(f"学历: {job.education}")
        print(f"经验: {job.experience}")
        print(f"技能: {job.tags}")
        print(f"福利: {job.welfare}")

    else:
        print("✗ 数据库中没有职位数据")
        print("请先运行爬虫或导入数据")

except Exception as e:
    print(f"✗ 错误: {str(e)}")
    import traceback
    traceback.print_exc()
