"""
更新公司类型和规模数据
"""

from _bootstrap import PROJECT_ROOT
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Company

# 定义公司类型判断规则
def determine_company_type(company_name):
    """根据公司名称判断公司类型"""
    name = company_name.lower()

    # 上市公司关键词
    if any(keyword in name for keyword in ['腾讯', '阿里', '百度', '字节', '美团', '京东', '网易', '小米', '华为', '滴滴', '拼多多', '快手', 'bilibili', 'b站', '蚂蚁', '携程', '58', '新浪', '搜狐', '360']):
        return '上市公司'

    # 国企关键词
    if any(keyword in name for keyword in ['中国', '国家', '中央', '人民', '国有', '集团', '银行', '电信', '移动', '联通', '石油', '石化', '电网', '铁路', '航空', '邮政']):
        return '国企'

    # 外企关键词
    if any(keyword in name for keyword in ['microsoft', 'google', 'amazon', 'facebook', 'apple', 'intel', 'ibm', 'oracle', 'sap', 'cisco', 'dell', 'hp', 'samsung', 'lg', 'sony', '微软', '谷歌', '亚马逊', '甲骨文', '思科']):
        return '外企'

    # 创业公司关键词（通常是较新的科技公司）
    if any(keyword in name for keyword in ['科技有限', '信息技术', '网络科技', '智能科技', '数据科技', '软件科技', 'tech', 'ai', '人工智能', '区块链']):
        # 随机分配一些为创业公司
        if random.random() < 0.3:
            return '创业公司'
        return '民营'

    # 默认为民营
    return '民营'

def determine_company_size(company_type):
    """根据公司类型分配公司规模"""
    if company_type == '上市公司':
        # 上市公司通常规模较大
        return random.choice(['1000-9999人', '10000人以上'])
    elif company_type == '国企':
        # 国企通常规模中大型
        return random.choice(['500-999人', '1000-9999人', '10000人以上'])
    elif company_type == '外企':
        # 外企规模中等偏大
        return random.choice(['100-499人', '500-999人', '1000-9999人'])
    elif company_type == '创业公司':
        # 创业公司规模较小
        return random.choice(['20人以下', '20-99人', '100-499人'])
    else:  # 民营
        # 民营企业规模分布较广
        return random.choice(['20-99人', '100-499人', '500-999人', '1000-9999人'])

def update_companies():
    """更新所有公司的类型和规模"""
    companies = list(Company.objects.all())
    updated_count = 0

    print(f"总共 {len(companies)} 家公司需要更新\n")

    # 为了让数据更丰富，手动分配一些公司类型
    # 选择一些公司作为外企、国企、创业公司
    company_count = len(companies)

    # 计算各类型数量（目标分布）
    target_distribution = {
        '上市公司': int(company_count * 0.35),  # 35%
        '民营': int(company_count * 0.30),      # 30%
        '创业公司': int(company_count * 0.20),   # 20%
        '外企': int(company_count * 0.10),      # 10%
        '国企': int(company_count * 0.05),      # 5%
    }

    # 已分配的公司类型计数
    type_counts = {'上市公司': 0, '民营': 0, '创业公司': 0, '外企': 0, '国企': 0}

    for company in companies:
        old_type = company.company_type
        old_size = company.company_size

        # 确定新的公司类型
        basic_type = determine_company_type(company.name)

        # 如果基础判断是上市公司或民营，根据配额调整
        if basic_type in ['上市公司', '民营']:
            # 如果某个类型还没达到目标，优先分配
            for type_name in ['创业公司', '外企', '国企', '民营', '上市公司']:
                if type_counts[type_name] < target_distribution[type_name]:
                    new_type = type_name
                    break
            else:
                new_type = basic_type
        else:
            new_type = basic_type

        type_counts[new_type] += 1
        company.company_type = new_type

        # 确定新的公司规模
        new_size = determine_company_size(new_type)
        company.company_size = new_size

        company.save()
        updated_count += 1

        print(f"{updated_count}. {company.name}")
        print(f"   类型: {old_type} -> {new_type}")
        print(f"   规模: {old_size} -> {new_size}")
        print()

    print(f"\n成功更新 {updated_count} 家公司")

    # 统计更新后的分布
    from collections import Counter
    types = Counter([c.company_type for c in Company.objects.all()])
    sizes = Counter([c.company_size for c in Company.objects.all()])

    print("\n更新后的公司类型分布:")
    for type_name, count in types.most_common():
        print(f"  {type_name}: {count}")

    print("\n更新后的公司规模分布:")
    for size_name, count in sizes.most_common():
        print(f"  {size_name}: {count}")

if __name__ == '__main__':
    update_companies()
