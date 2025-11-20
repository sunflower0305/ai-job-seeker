"""
生成模拟招聘数据
用于测试后续的数据处理、分析、可视化等功能
"""

import json
import random
from datetime import datetime, timedelta


# 数据模板
CITIES = ['北京', '上海', '深圳', '广州', '杭州', '成都', '武汉', '南京', '西安', '重庆']
JOB_TITLES = [
    'Python开发工程师', 'Java开发工程师', 'Web前端工程师', '数据分析师',
    '算法工程师', '测试工程师', '产品经理', 'UI设计师',
    '运维工程师', 'Android开发工程师', 'iOS开发工程师', '大数据工程师',
    '人工智能工程师', '后端开发工程师', '全栈工程师', '架构师'
]
COMPANIES = [
    '阿里巴巴', '腾讯', '字节跳动', '百度', '京东',
    '美团', '网易', '滴滴', '小米', '华为',
    '拼多多', '快手', '新浪', '搜狐', '360',
    '科技有限公司', '互联网科技', '信息技术公司', '软件开发公司', '数据科技'
]
EXPERIENCES = ['不限', '1-3年', '3-5年', '5-10年', '10年以上']
EDUCATIONS = ['不限', '大专', '本科', '硕士', '博士']
COMPANY_SIZES = ['0-20人', '20-99人', '100-499人', '500-999人', '1000-9999人', '10000人以上']
COMPANY_TYPES = ['民营企业', '上市公司', '外资企业', '国企', '创业公司']
INDUSTRIES = ['互联网', '电子商务', '金融', '教育', '医疗健康', '游戏', '企业服务', '人工智能', '大数据', '云计算']
SKILLS = ['Python', 'Java', 'JavaScript', 'React', 'Vue', 'Django', 'Flask', 'Spring', 'MySQL', 'Redis',
          'MongoDB', 'Docker', 'Kubernetes', 'Linux', 'Git', 'HTML', 'CSS', 'Node.js', 'Go', 'C++']
WELFARES = ['五险一金', '年终奖', '股票期权', '弹性工作', '带薪年假', '节日福利', '定期体检',
            '免费三餐', '下午茶', '员工旅游', '通讯补贴', '交通补贴', '租房补贴', '员工培训']


def generate_salary(job_title, city, education, experience):
    """
    根据职位、城市、学历、经验生成薪资
    """
    # 基础薪资
    base_salary = {
        '北京': 12000, '上海': 11000, '深圳': 11000, '广州': 9000, '杭州': 10000,
        '成都': 8000, '武汉': 7500, '南京': 8500, '西安': 7000, '重庆': 7500
    }

    # 职位系数
    job_coefficient = {
        'Python': 1.0, 'Java': 1.0, 'Web前端': 0.9, '数据分析': 1.1,
        '算法': 1.3, '测试': 0.8, '产品': 0.9, 'UI设计': 0.85,
        '运维': 0.9, 'Android': 0.95, 'iOS': 0.95, '大数据': 1.2,
        '人工智能': 1.4, '后端': 1.0, '全栈': 1.15, '架构': 1.5
    }

    # 学历系数
    edu_coefficient = {
        '不限': 0.8, '大专': 0.85, '本科': 1.0, '硕士': 1.2, '博士': 1.4
    }

    # 经验系数
    exp_coefficient = {
        '不限': 0.7, '1-3年': 1.0, '3-5年': 1.3, '5-10年': 1.6, '10年以上': 2.0
    }

    # 计算薪资
    base = base_salary.get(city, 8000)

    # 查找职位系数
    job_coef = 1.0
    for key in job_coefficient:
        if key in job_title:
            job_coef = job_coefficient[key]
            break

    salary_mid = base * job_coef * edu_coefficient[education] * exp_coefficient[experience]

    # 添加随机波动
    salary_mid = salary_mid * random.uniform(0.9, 1.1)

    # 计算最低和最高薪资（±20%）
    salary_min = int(salary_mid * 0.8 / 1000) * 1000
    salary_max = int(salary_mid * 1.2 / 1000) * 1000

    return salary_min, salary_max


def generate_job_description(job_title, skills):
    """生成职位描述"""
    descriptions = [
        f"负责{job_title}相关工作，参与项目开发和维护",
        f"使用{', '.join(skills[:3])}等技术进行系统开发",
        "参与需求分析、系统设计、编码实现和测试工作",
        "与团队协作，保证项目按时交付",
        "编写技术文档，进行代码审查",
        "持续优化系统性能，解决技术难题"
    ]
    return '；'.join(random.sample(descriptions, 4)) + '。'


def generate_mock_jobs(count=500):
    """
    生成模拟职位数据

    Args:
        count: 生成数据条数

    Returns:
        list: 职位数据列表
    """
    jobs = []

    for i in range(count):
        city = random.choice(CITIES)
        job_title = random.choice(JOB_TITLES)
        company_name = random.choice(COMPANIES)
        education = random.choice(EDUCATIONS)
        experience = random.choice(EXPERIENCES)

        # 生成薪资
        salary_min, salary_max = generate_salary(job_title, city, education, experience)

        # 随机选择技能
        job_skills = random.sample(SKILLS, random.randint(3, 6))

        # 生成职位
        job = {
            'job_title': job_title,
            'company_name': company_name if i % 5 != 0 else f"{company_name}科技有限公司",
            'salary_min': salary_min,
            'salary_max': salary_max,
            'salary_months': random.choice([12, 13, 14, 15, 16]),
            'city': city,
            'experience': experience,
            'education': education,
            'company_size': random.choice(COMPANY_SIZES),
            'company_type': random.choice(COMPANY_TYPES),
            'industry': random.choice(INDUSTRIES),
            'job_description': generate_job_description(job_title, job_skills),
            'job_tags': ','.join(job_skills),
            'welfare': ','.join(random.sample(WELFARES, random.randint(4, 8))),
            'source': random.choice(['Boss直聘', '智联招聘', '前程无忧', '拉勾网']),
            'url': f"https://example.com/job/{i+1}",
            'publish_time': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S'),
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        jobs.append(job)

    return jobs


def save_to_json(jobs, filename='data/raw/mock_jobs.json'):
    """保存数据到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"✓ 已生成 {len(jobs)} 条模拟数据")
    print(f"✓ 保存到: {filename}")


def print_statistics(jobs):
    """打印统计信息"""
    print("\n" + "="*60)
    print("数据统计")
    print("="*60)

    # 城市分布
    city_count = {}
    for job in jobs:
        city = job['city']
        city_count[city] = city_count.get(city, 0) + 1

    print(f"\n城市分布:")
    for city, count in sorted(city_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {city}: {count} 条")

    # 薪资统计
    salaries = [(job['salary_min'] + job['salary_max']) / 2 for job in jobs]
    print(f"\n薪资统计:")
    print(f"  平均薪资: {int(sum(salaries) / len(salaries))} 元/月")
    print(f"  最高薪资: {int(max(salaries))} 元/月")
    print(f"  最低薪资: {int(min(salaries))} 元/月")

    # 学历分布
    edu_count = {}
    for job in jobs:
        edu = job['education']
        edu_count[edu] = edu_count.get(edu, 0) + 1

    print(f"\n学历要求分布:")
    for edu, count in sorted(edu_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {edu}: {count} 条 ({count/len(jobs)*100:.1f}%)")

    # 经验分布
    exp_count = {}
    for job in jobs:
        exp = job['experience']
        exp_count[exp] = exp_count.get(exp, 0) + 1

    print(f"\n经验要求分布:")
    for exp, count in sorted(exp_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {exp}: {count} 条 ({count/len(jobs)*100:.1f}%)")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("生成模拟招聘数据")
    print("="*60)

    # 生成500条数据
    jobs = generate_mock_jobs(500)

    # 保存数据
    save_to_json(jobs)

    # 显示样例
    print("\n" + "="*60)
    print("数据样例（前3条）")
    print("="*60)
    for i, job in enumerate(jobs[:3], 1):
        print(f"\n职位 {i}:")
        print(f"  职位: {job['job_title']}")
        print(f"  公司: {job['company_name']}")
        print(f"  薪资: {job['salary_min']}-{job['salary_max']} 元/月 × {job['salary_months']}薪")
        print(f"  城市: {job['city']}")
        print(f"  经验: {job['experience']}")
        print(f"  学历: {job['education']}")
        print(f"  技能: {job['job_tags']}")

    # 统计信息
    print_statistics(jobs)

    print("\n" + "="*60)
    print("✓ 模拟数据生成完成！")
    print("="*60)
    print("\n说明:")
    print("  - 这些数据可用于后续的数据清洗、分析、可视化等功能开发")
    print("  - 数据完全模拟真实场景，包含所有必要字段")
    print("  - 可以用这些数据继续开发，不影响项目进度")


if __name__ == '__main__':
    main()
