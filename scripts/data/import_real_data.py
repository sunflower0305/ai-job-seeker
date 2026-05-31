#!/usr/bin/env python3
"""
直接导入真实爬虫数据
"""

from _bootstrap import PROJECT_ROOT

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job, Company

def import_real_data():
    """导入真实爬虫数据"""
    import json

    # 使用处理后的数据文件
    data_file = 'data/processed/demo_cleaned_jobs.json'

    print(f"\n{'='*60}")
    print(f"开始导入真实爬虫数据")
    print(f"{'='*60}")
    print(f"数据文件: {data_file}")

    with open(data_file, 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)

    print(f"读取到 {len(jobs_data)} 条职位数据\n")

    # 清空旧数据
    print("清空旧数据...")
    Job.objects.all().delete()
    Company.objects.all().delete()

    created_companies = 0
    created_jobs = 0

    for i, job_data in enumerate(jobs_data, 1):
        try:
            # 创建或获取公司
            company_name = job_data.get('company_name', '未知公司')
            company, created = Company.objects.get_or_create(
                name=company_name,
                defaults={
                    'industry': job_data.get('industry', ''),
                    'company_size': job_data.get('company_size', ''),
                    'company_type': job_data.get('company_type', ''),
                    'description': f"{company_name}是一家优秀的企业",
                }
            )
            if created:
                created_companies += 1

            # 处理职位标题和城市
            job_title = job_data.get('job_title', '').strip()
            if '\n' in job_title:
                job_title = job_title.split('\n')[0].strip()

            city = job_data.get('city', '').strip()

            # 提取技能标签
            tags = []
            job_tags = job_data.get('job_tags', '')
            if job_tags:
                if isinstance(job_tags, str):
                    tags = [tag.strip() for tag in job_tags.split(',') if tag.strip()]
                elif isinstance(job_tags, list):
                    tags = job_tags

            # 额外从技能分类中提取
            for skill_category in ['skills_languages', 'skills_web_frameworks', 'skills_databases',
                                   'skills_big_data', 'skills_ml_ai', 'skills_devops', 'skills_mobile']:
                skills = job_data.get(skill_category, '')
                if skills:
                    category_tags = [tag.strip() for tag in skills.split(',') if tag.strip()]
                    tags.extend(category_tags)

            # 去重
            tags = list(set(tags))

            # 创建职位
            Job.objects.create(
                title=job_title,
                company=company,
                city=city,
                salary_min=int(job_data.get('salary_min', 0) or 0),
                salary_max=int(job_data.get('salary_max', 0) or 0),
                salary_months=int(job_data.get('salary_months', 12) or 12),
                experience=job_data.get('experience', '不限'),
                education=job_data.get('education', '不限'),
                description=job_data.get('job_description', ''),
                requirements='',
                welfare=job_data.get('welfare', '五险一金、带薪年假'),
                source_url=job_data.get('url', ''),
                tags=tags,
                is_active=True,
            )

            created_jobs += 1
            if created_jobs % 50 == 0:
                print(f"已导入 {created_jobs} 个职位...")

        except Exception as e:
            print(f"导入第 {i} 条数据时出错: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\n{'='*60}")
    print("导入完成！")
    print(f"{'='*60}")
    print(f"新增公司: {created_companies}")
    print(f"新增职位: {created_jobs}")
    print(f"\n数据库统计:")
    print(f"  总公司数: {Company.objects.count()}")
    print(f"  总职位数: {Job.objects.count()}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    import_real_data()
