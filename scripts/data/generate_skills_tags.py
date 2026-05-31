#!/usr/bin/env python3
"""
为职位数据生成技能标签
"""

from _bootstrap import PROJECT_ROOT
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job

# 定义职位类型与技能的映射
SKILLS_MAP = {
    # 开发类
    'Python': ['Python', 'Django', 'Flask', 'FastAPI', 'SQLAlchemy', 'Pandas', 'NumPy'],
    'Java': ['Java', 'Spring', 'SpringBoot', 'MyBatis', 'Maven', 'Gradle'],
    '前端': ['JavaScript', 'HTML', 'CSS', 'Vue', 'React', 'Angular', 'TypeScript', 'Webpack'],
    'Web': ['JavaScript', 'HTML', 'CSS', 'Vue', 'React', 'Node.js', 'TypeScript'],
    '后端': ['Java', 'Python', 'Go', 'MySQL', 'Redis', 'Kafka', 'Docker'],
    '全栈': ['JavaScript', 'Python', 'Vue', 'React', 'Node.js', 'MySQL', 'Docker'],
    'Android': ['Java', 'Kotlin', 'Android SDK', 'Jetpack', 'MVVM'],
    'iOS': ['Swift', 'Objective-C', 'UIKit', 'SwiftUI', 'Xcode'],
    '移动': ['React Native', 'Flutter', 'Dart', 'Kotlin', 'Swift'],

    # 数据类
    '数据': ['Python', 'SQL', 'Pandas', 'NumPy', 'Matplotlib', 'Tableau'],
    '算法': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Keras'],
    '机器学习': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy'],
    '深度学习': ['Python', 'TensorFlow', 'PyTorch', 'Keras', 'CUDA'],
    'AI': ['Python', 'TensorFlow', 'PyTorch', 'NLP', '计算机视觉'],

    # 运维类
    '运维': ['Linux', 'Shell', 'Docker', 'Kubernetes', 'Jenkins', 'Ansible', 'Prometheus'],
    'DevOps': ['Linux', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'CI/CD'],
    '测试': ['Selenium', 'Pytest', 'JUnit', 'Postman', 'Jmeter', 'Appium'],

    # 架构类
    '架构': ['微服务', '分布式', '高并发', '系统设计', 'Redis', 'Kafka', 'Elasticsearch'],
    '系统': ['Linux', 'C++', '操作系统', '网络协议', 'TCP/IP'],

    # 产品类
    '产品': ['Axure', 'Sketch', 'Figma', '原型设计', '需求分析', 'PRD'],
    '设计': ['Photoshop', 'Sketch', 'Figma', 'UI设计', 'UX设计'],

    # 大数据类
    '大数据': ['Hadoop', 'Spark', 'Hive', 'Flink', 'Kafka', 'Scala'],

    # 通用技能
    '工程师': ['Git', 'Linux', 'Docker', 'MySQL', 'Redis'],
}

def get_skills_for_job(title, description=''):
    """根据职位标题和描述推断技能标签"""
    skills = set()

    # 根据标题匹配
    title_lower = title.lower()

    for keyword, skill_list in SKILLS_MAP.items():
        if keyword.lower() in title_lower or keyword in title:
            skills.update(skill_list)

    # 添加通用技能
    if '工程师' in title or 'engineer' in title_lower:
        skills.update(['Git', 'Linux'])

    # 添加数据库相关
    if any(word in title_lower for word in ['后端', '全栈', '开发']):
        skills.update(['MySQL', 'Redis'])

    # 限制技能数量
    skills = list(skills)[:8]

    # 如果没有匹配到技能，添加一些默认技能
    if not skills:
        if '产品' in title:
            skills = ['需求分析', '原型设计', 'Axure', 'PRD']
        elif '设计' in title:
            skills = ['Photoshop', 'Sketch', 'UI设计']
        elif '运营' in title:
            skills = ['数据分析', '活动策划', '用户运营']
        elif '销售' in title or '市场' in title:
            skills = ['市场营销', '销售技巧', '客户关系']
        else:
            skills = ['Office', '沟通能力', '团队协作']

    return skills

def main():
    """主函数"""
    print("开始为职位生成技能标签...")

    jobs = Job.objects.all()
    total = jobs.count()
    updated = 0

    for i, job in enumerate(jobs, 1):
        # 获取技能标签
        skills = get_skills_for_job(job.title, job.description)

        # 更新职位
        if skills:
            job.tags = skills
            job.save(update_fields=['tags'])
            updated += 1
            print(f"[{i}/{total}] {job.title} -> {', '.join(skills)}")
        else:
            print(f"[{i}/{total}] {job.title} -> 无技能")

    print(f"\n完成！共更新 {updated}/{total} 个职位的技能标签")

    # 统计技能分布
    from collections import Counter
    skills_counter = Counter()
    for job in Job.objects.all():
        if job.tags:
            for skill in job.tags:
                skills_counter[skill] += 1

    print(f"\n技能统计 Top 20:")
    for skill, count in skills_counter.most_common(20):
        print(f"  {skill}: {count}")

if __name__ == '__main__':
    main()
