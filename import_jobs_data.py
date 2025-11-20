#!/usr/bin/env python3
"""
导入清洗后的职位数据到Django数据库
"""

import os
import sys
import django
import json
from pathlib import Path
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job, Company


def import_jobs_from_json(json_file):
    """从JSON文件导入职位数据"""

    print(f"\n{'='*60}")
    print(f"开始导入职位数据")
    print(f"{'='*60}")
    print(f"数据文件: {json_file}")

    # 读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)

    print(f"读取到 {len(jobs_data)} 条职位数据\n")

    # 统计
    created_companies = 0
    created_jobs = 0
    skipped_jobs = 0

    for i, job_data in enumerate(jobs_data, 1):
        try:
            # 创建或获取公司
            company_name = job_data.get('company_name', '未知公司')
            company, created = Company.objects.get_or_create(
                name=company_name,
                defaults={
                    'industry': job_data.get('industry', ''),
                    'scale': job_data.get('company_size', ''),
                    'description': f"{company_name}是一家优秀的企业",
                }
            )
            if created:
                created_companies += 1

            # 创建职位
            job, created = Job.objects.get_or_create(
                title=job_data.get('job_title', ''),
                company=company,
                location=job_data.get('city', '') + '-' + job_data.get('district', ''),
                defaults={
                    'salary_min': job_data.get('salary_min', 0),
                    'salary_max': job_data.get('salary_max', 0),
                    'experience': job_data.get('experience', ''),
                    'education': job_data.get('education', ''),
                    'job_type': job_data.get('job_type', '全职'),
                    'description': job_data.get('job_description', ''),
                    'requirements': job_data.get('job_requirements', ''),
                    'responsibilities': job_data.get('job_responsibilities', ''),
                    'benefits': '五险一金、带薪年假、定期体检、员工培训',
                    'url': job_data.get('url', ''),
                }
            )

            if created:
                created_jobs += 1
                if created_jobs % 10 == 0:
                    print(f"已导入 {created_jobs} 个职位...")
            else:
                skipped_jobs += 1

        except Exception as e:
            print(f"导入第 {i} 条数据时出错: {e}")
            continue

    # 打印统计信息
    print(f"\n{'='*60}")
    print("导入完成！")
    print(f"{'='*60}")
    print(f"新增公司: {created_companies}")
    print(f"新增职位: {created_jobs}")
    print(f"跳过职位: {skipped_jobs}")
    print(f"\n数据库统计:")
    print(f"  总公司数: {Company.objects.count()}")
    print(f"  总职位数: {Job.objects.count()}")
    print(f"{'='*60}\n")


def main():
    """主函数"""

    # 查找最新的清洗数据文件
    data_dir = Path('data/processed')
    json_files = list(data_dir.glob('*cleaned_jobs*.json'))

    if not json_files:
        print("错误: 未找到清洗后的数据文件")
        print("请先运行数据清洗脚本")
        return

    # 使用最新的文件
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)

    print("\n可用的数据文件:")
    for i, file in enumerate(json_files, 1):
        size = file.stat().st_size / 1024  # KB
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        marker = " ← 最新" if file == latest_file else ""
        print(f"{i}. {file.name} ({size:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M')}) {marker}")

    # 选择文件
    choice = input(f"\n请选择要导入的文件 (1-{len(json_files)}, 直接回车使用最新): ").strip()

    if choice == '':
        selected_file = latest_file
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(json_files):
                selected_file = json_files[idx]
            else:
                print("无效选择，使用最新文件")
                selected_file = latest_file
        except ValueError:
            print("无效输入，使用最新文件")
            selected_file = latest_file

    # 确认导入
    print(f"\n将导入文件: {selected_file.name}")
    confirm = input("确认导入？(y/n): ").lower().strip()

    if confirm != 'y':
        print("已取消导入")
        return

    # 执行导入
    import_jobs_from_json(selected_file)


if __name__ == '__main__':
    main()
