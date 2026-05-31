#!/usr/bin/env python
"""
检查数据库职位数据和推荐功能
"""

from _bootstrap import PROJECT_ROOT
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job, Company
from jobs.ai_analyzer import JobRecommender

print("=== 数据库职位数据检查 ===\n")

# 1. 检查职位总数
total_jobs = Job.objects.filter(is_active=True).count()
total_companies = Company.objects.count()

print(f"活跃职位总数: {total_jobs}")
print(f"公司总数: {total_companies}\n")

if total_jobs == 0:
    print("❌ 数据库中没有职位数据！")
    print("建议：运行爬虫获取数据")
    exit()

# 2. 按城市统计
print("=== 按城市统计 ===")
from django.db.models import Count
city_stats = Job.objects.filter(is_active=True).values('city').annotate(count=Count('id')).order_by('-count')[:10]
for stat in city_stats:
    print(f"{stat['city']:10} : {stat['count']} 个职位")

# 3. 按技能统计
print("\n=== 热门技能 ===")
from collections import Counter
skills_counter = Counter()
for job in Job.objects.filter(is_active=True)[:1000]:  # 取前1000个职位
    if job.tags:
        for skill in job.tags:
            if skill:
                skills_counter[skill] += 1

for skill, count in skills_counter.most_common(20):
    print(f"{skill:15} : {count}")

# 4. 测试搜索功能
print("\n=== 测试搜索功能 ===")

# 测试1: 搜索Python职位
python_jobs = Job.objects.filter(is_active=True, tags__icontains='Python')[:5]
print(f"\n包含Python的职位: {python_jobs.count()} 个")
for job in python_jobs[:3]:
    print(f"  - {job.title} ({job.company.name}) - {job.city}")

# 测试2: 搜索Java职位
java_jobs = Job.objects.filter(is_active=True, tags__icontains='Java')[:5]
print(f"\n包含Java的职位: {java_jobs.count()} 个")
for job in java_jobs[:3]:
    print(f"  - {job.title} ({job.company.name}) - {job.city}")

# 5. 测试AI推荐器
print("\n=== 测试AI推荐器 ===")
try:
    # 模拟简历分析结果
    resume_analysis = {
        'skills': ['Python', 'Django', 'MySQL'],
        'experience_years': 3,
        'education': '本科',
        'desired_position': 'Python开发工程师',
        'desired_salary': '15000-25000',
        'key_strengths': ['后端开发', 'API设计', '数据库优化'],
        'work_experience': '3年Python开发经验'
    }

    print("简历信息:")
    print(f"  技能: {', '.join(resume_analysis['skills'])}")
    print(f"  经验: {resume_analysis['experience_years']}年")
    print(f"  学历: {resume_analysis['education']}")
    print(f"  期望职位: {resume_analysis['desired_position']}")

    print("\n正在测试推荐功能...")
    print("注意: 这需要调用通义千问API，请确保API配置正确\n")

    # 测试推荐器
    recommender = JobRecommender()
    result = recommender.recommend_jobs(resume_analysis)

    if result.get('success'):
        print("✓ AI推荐成功！")
        print(f"\n推荐结果:\n{result.get('recommendation', '')[:500]}...")
    else:
        print(f"✗ AI推荐失败: {result.get('error', '未知错误')}")

except Exception as e:
    print(f"✗ 测试推荐器时出错: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n=== 检查完成 ===")
