#!/usr/bin/env python3
"""
清理数据库中的假数据，只保留真实公司的职位
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job, Company

# 定义假公司名称列表（这些是生成的假数据）
FAKE_COMPANY_NAMES = [
    '互联网科技',
    '数据科技',
    '软件开发公司',
    '信息技术公司',
    '科技有限公司',
    '科技有限公司科技有限公司',  # 重复的假名
    '软件开发公司科技有限公司',
    '互联网科技科技有限公司',
    '数据科技科技有限公司',
    '信息技术公司科技有限公司',
]

# 真实公司名称（保留这些）
REAL_COMPANY_NAMES = [
    '阿里巴巴', '腾讯', '字节跳动', '美团', '京东', '拼多多',
    '华为', '小米', '百度', '网易', '快手', '滴滴', '360',
    '新浪', '搜狐', '携程', '去哪儿', '爱奇艺', '58同城',
    # 带后缀的也保留
    '阿里巴巴科技有限公司', '腾讯科技有限公司', '华为科技有限公司',
    '小米科技有限公司', '拼多多科技有限公司', '搜狐科技有限公司',
    '网易科技有限公司', '新浪科技有限公司', '美团科技有限公司',
    # 猎聘爬取的真实公司
    '和利时科技集团',
    '北方集成电路技术创新中心(北京)有限公司',
    'HUNGRY STUDIO',
]


def clean_fake_data():
    """清理假数据"""

    print("\n" + "="*80)
    print("开始清理假数据")
    print("="*80)

    # 统计当前数据
    total_companies = Company.objects.count()
    total_jobs = Job.objects.count()

    print(f"\n当前数据库状态:")
    print(f"  公司总数: {total_companies}")
    print(f"  职位总数: {total_jobs}")

    # 查找假公司
    fake_companies = Company.objects.filter(name__in=FAKE_COMPANY_NAMES)
    fake_company_count = fake_companies.count()

    print(f"\n发现假公司: {fake_company_count} 家")
    for company in fake_companies:
        job_count = Job.objects.filter(company=company).count()
        print(f"  - {company.name}: {job_count}个职位")

    # 确认删除
    print(f"\n将要删除 {fake_company_count} 家假公司及其相关的职位")
    confirm = input("确认删除？(yes/no): ").lower().strip()

    if confirm != 'yes':
        print("已取消删除")
        return

    # 删除假公司及相关职位
    deleted_jobs = 0
    for company in fake_companies:
        job_count = Job.objects.filter(company=company).count()
        Job.objects.filter(company=company).delete()
        deleted_jobs += job_count

    deleted_companies = fake_companies.count()
    fake_companies.delete()

    # 显示结果
    remaining_companies = Company.objects.count()
    remaining_jobs = Job.objects.count()

    print("\n" + "="*80)
    print("清理完成！")
    print("="*80)
    print(f"删除公司: {deleted_companies}")
    print(f"删除职位: {deleted_jobs}")
    print(f"\n剩余数据:")
    print(f"  公司总数: {remaining_companies}")
    print(f"  职位总数: {remaining_jobs}")

    print("\n剩余公司列表:")
    for i, company in enumerate(Company.objects.all()[:30], 1):
        job_count = Job.objects.filter(company=company).count()
        print(f"  {i}. {company.name}: {job_count}个职位 ({company.industry or '未知行业'})")

    print("="*80 + "\n")


if __name__ == '__main__':
    clean_fake_data()
