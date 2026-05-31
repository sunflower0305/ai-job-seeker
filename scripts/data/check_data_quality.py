#!/usr/bin/env python3
"""
检查数据质量报告
"""

from _bootstrap import PROJECT_ROOT

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job, Company
from collections import Counter


def check_data_quality():
    """生成数据质量报告"""

    print("\n" + "="*80)
    print("数据质量检查报告")
    print("="*80)

    # 1. 基础统计
    total_companies = Company.objects.count()
    total_jobs = Job.objects.count()

    print(f"\n【基础统计】")
    print(f"  公司总数: {total_companies}")
    print(f"  职位总数: {total_jobs}")

    # 2. 公司名称分析
    print(f"\n【公司名称分析】")

    # 可疑的假公司名（过于通用）
    suspicious_keywords = ['互联网科技', '数据科技', '软件开发公司', '信息技术公司', '科技有限公司科技']
    suspicious_companies = []

    for keyword in suspicious_keywords:
        companies = Company.objects.filter(name__icontains=keyword)
        if companies.exists():
            for company in companies:
                job_count = Job.objects.filter(company=company).count()
                suspicious_companies.append((company.name, job_count))

    if suspicious_companies:
        print(f"\n  ⚠️  发现 {len(suspicious_companies)} 家可疑公司（可能是假数据）:")
        for name, count in sorted(suspicious_companies, key=lambda x: -x[1]):
            print(f"    - {name}: {count}个职位")

    # 真实公司
    real_company_keywords = ['阿里巴巴', '腾讯', '字节跳动', '美团', '京东', '拼多多',
                              '华为', '小米', '百度', '网易', '快手', '滴滴', '360',
                              '新浪', '搜狐']
    real_companies = []

    for keyword in real_company_keywords:
        companies = Company.objects.filter(name__icontains=keyword)
        for company in companies:
            job_count = Job.objects.filter(company=company).count()
            real_companies.append((company.name, job_count))

    if real_companies:
        print(f"\n  ✓ 发现 {len(real_companies)} 家真实知名公司:")
        for name, count in sorted(real_companies, key=lambda x: -x[1])[:15]:
            print(f"    - {name}: {count}个职位")

    # 3. 数据完整性检查
    print(f"\n【数据完整性检查】")

    jobs = Job.objects.all()
    no_salary_count = jobs.filter(salary_min__isnull=True).count() + jobs.filter(salary_min=0).count()
    no_city_count = jobs.filter(city='').count() + jobs.filter(city__isnull=True).count()
    no_description_count = jobs.filter(description='').count() + jobs.filter(description__isnull=True).count()

    print(f"  缺少薪资信息: {no_salary_count}/{total_jobs} ({no_salary_count/total_jobs*100:.1f}%)")
    print(f"  缺少城市信息: {no_city_count}/{total_jobs} ({no_city_count/total_jobs*100:.1f}%)")
    print(f"  缺少职位描述: {no_description_count}/{total_jobs} ({no_description_count/total_jobs*100:.1f}%)")

    # 4. 数据来源分析
    print(f"\n【建议】")

    fake_count = len(suspicious_companies)
    real_count = len(real_companies)

    if fake_count > 0:
        print(f"  ⚠️  数据库中包含 {fake_count} 家可疑的假公司")
        print(f"  ✓ 建议运行 scripts/data/clean_fake_data.py 清理假数据")

    if no_salary_count > total_jobs * 0.3:
        print(f"  ⚠️  超过30%的职位缺少薪资信息")
        print(f"  ✓ 建议重新爬取数据或优化数据清洗脚本")

    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    check_data_quality()
