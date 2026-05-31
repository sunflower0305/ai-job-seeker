#!/usr/bin/env python3
"""
生成模拟的用户访问和AI调用数据用于测试统计功能
"""

from _bootstrap import PROJECT_ROOT

import os
import sys
import django
from datetime import datetime, timedelta
import random

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from users.models import User, UserAccessLog, AICallLog

def generate_test_data():
    """生成测试数据"""

    print("开始生成测试数据...")

    # 获取所有用户
    users = list(User.objects.all())
    if not users:
        print("没有找到用户，请先创建一些用户")
        return

    print(f"找到 {len(users)} 个用户")

    # 生成最近30天的数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # 1. 生成用户访问日志
    print("\n生成用户访问日志...")
    access_paths = [
        '/api/jobs/jobs/',
        '/api/jobs/jobs/1/',
        '/api/jobs/jobs/2/',
        '/api/users/me/',
        '/api/users/me/profile/',
        '/api/jobs/collections/',
        '/api/jobs/applications/',
    ]

    access_count = 0
    current_date = start_date
    while current_date <= end_date:
        # 每天生成10-50条访问记录
        daily_count = random.randint(10, 50)
        for _ in range(daily_count):
            user = random.choice(users + [None])  # 有些访问可能是匿名的
            path = random.choice(access_paths)

            # 随机生成当天的某个时间
            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            random_second = random.randint(0, 59)
            log_time = current_date.replace(
                hour=random_hour,
                minute=random_minute,
                second=random_second
            )

            UserAccessLog.objects.create(
                user=user,
                path=path,
                method='GET',
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                created_at=log_time
            )
            access_count += 1

        current_date += timedelta(days=1)

    print(f"生成了 {access_count} 条访问日志")

    # 2. 生成AI调用日志
    print("\n生成AI调用日志...")
    call_types = ['recommendation', 'chat', 'analysis', 'other']
    model_names = ['gpt-3.5-turbo', 'gpt-4', 'deepseek-chat']

    ai_call_count = 0
    current_date = start_date
    while current_date <= end_date:
        # 每天生成5-20条AI调用记录
        daily_count = random.randint(5, 20)
        for _ in range(daily_count):
            user = random.choice(users + [None])
            call_type = random.choice(call_types)
            model_name = random.choice(model_names)

            # 生成token数
            prompt_tokens = random.randint(100, 1000)
            completion_tokens = random.randint(50, 500)
            total_tokens = prompt_tokens + completion_tokens

            # 响应时间（秒）
            response_time = round(random.uniform(0.5, 5.0), 2)

            # 90%的成功率
            success = random.random() < 0.9
            error_message = "" if success else "API调用失败"

            # 随机生成当天的某个时间
            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            random_second = random.randint(0, 59)
            log_time = current_date.replace(
                hour=random_hour,
                minute=random_minute,
                second=random_second
            )

            AICallLog.objects.create(
                user=user,
                call_type=call_type,
                model_name=model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                response_time=response_time,
                success=success,
                error_message=error_message,
                created_at=log_time
            )
            ai_call_count += 1

        current_date += timedelta(days=1)

    print(f"生成了 {ai_call_count} 条AI调用日志")

    print("\n数据生成完成！")
    print(f"总计：")
    print(f"  - 用户访问日志: {access_count} 条")
    print(f"  - AI调用日志: {ai_call_count} 条")


if __name__ == '__main__':
    try:
        generate_test_data()
    except Exception as e:
        print(f"生成数据时出错: {e}")
        import traceback
        traceback.print_exc()
