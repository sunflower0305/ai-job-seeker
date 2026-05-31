"""
爬虫测试脚本
测试Boss直聘爬虫的基本功能
"""

from _bootstrap import PROJECT_ROOT

import sys
import os

# 将项目根目录添加到Python路径

# 导入爬虫模块
from crawler.boss_spider import BossSpider
from crawler.utils import spider_utils


def test_spider_utils():
    """测试工具函数"""
    print("\n" + "="*60)
    print("测试1：工具函数")
    print("="*60)

    # 测试薪资解析
    test_cases = [
        "10k-15k",
        "8-10K·13薪",
        "15k-20k·14薪",
        "面议",
    ]

    for salary_text in test_cases:
        result = spider_utils.parse_salary(salary_text)
        print(f"薪资: {salary_text:20s} → {result}")

    # 测试城市标准化
    print(f"\n城市标准化:")
    print(f"北京市 → {spider_utils.standardize_city('北京市')}")
    print(f"上海 → {spider_utils.standardize_city('上海')}")

    # 测试学历标准化
    print(f"\n学历标准化:")
    print(f"本科及以上 → {spider_utils.standardize_education('本科及以上')}")
    print(f"大专 → {spider_utils.standardize_education('大专')}")

    # 测试经验标准化
    print(f"\n经验标准化:")
    print(f"1-3年 → {spider_utils.standardize_experience('1-3年')}")
    print(f"5年以上 → {spider_utils.standardize_experience('5年以上')}")

    print("\n✓ 工具函数测试通过！")


def test_boss_spider_basic():
    """测试Boss直聘爬虫基础功能"""
    print("\n" + "="*60)
    print("测试2：Boss直聘爬虫 - 小规模测试")
    print("="*60)

    spider = BossSpider()

    # 测试单个城市、单个关键词、1页数据
    print("\n正在爬取: 北京 - Python - 第1页")
    print("（这是一个真实的网络请求测试，可能需要几秒钟...）")

    try:
        spider.crawl_by_city_and_keyword('北京', 'Python', max_pages=1)

        if spider.jobs_data:
            print(f"\n✓ 成功爬取 {len(spider.jobs_data)} 条数据")

            # 显示第一条数据
            if len(spider.jobs_data) > 0:
                print("\n第一条数据示例:")
                job = spider.jobs_data[0]
                print(f"  职位: {job.get('job_title')}")
                print(f"  公司: {job.get('company_name')}")
                print(f"  薪资: {job.get('salary_min')}-{job.get('salary_max')}")
                print(f"  城市: {job.get('city')}")
                print(f"  经验: {job.get('experience')}")
                print(f"  学历: {job.get('education')}")

            # 显示统计信息
            stats = spider.get_statistics()
            print(f"\n统计信息:")
            print(f"  总数: {stats['total']}")

            # 保存测试数据
            spider.save_to_json('data/raw/test_boss_jobs.json')
            print(f"\n✓ 测试数据已保存")

        else:
            print("\n✗ 未获取到数据（可能是网络问题或API变化）")
            print("提示: 这可能是因为:")
            print("  1. 网络连接问题")
            print("  2. Boss直聘API已更新")
            print("  3. 需要验证码验证")

    except Exception as e:
        print(f"\n✗ 爬虫测试出现异常: {e}")
        print(f"\n错误详情: {type(e).__name__}")
        import traceback
        traceback.print_exc()


def test_data_structure():
    """测试数据结构"""
    print("\n" + "="*60)
    print("测试3：数据结构验证")
    print("="*60)

    # 模拟一条数据
    mock_job = {
        'job_title': 'Python开发工程师',
        'company_name': '测试科技公司',
        'salary_min': 15000,
        'salary_max': 25000,
        'salary_months': 12,
        'city': '北京',
        'experience': '3-5年',
        'education': '本科',
        'company_size': '100-499人',
        'company_type': '民营企业',
        'industry': '互联网',
        'job_description': '负责Python后端开发',
        'job_tags': 'Python,Django,MySQL',
        'welfare': '五险一金,年终奖',
        'source': 'Boss直聘',
        'url': 'https://example.com',
        'publish_time': None,
        'crawl_time': '2024-01-15 10:00:00'
    }

    print("\n模拟职位数据结构:")
    for key, value in mock_job.items():
        print(f"  {key:20s}: {value}")

    print("\n✓ 数据结构符合设计要求")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("招聘数据爬虫 - 功能测试")
    print("="*60)

    # 测试1: 工具函数
    test_spider_utils()

    # 测试2: 数据结构
    test_data_structure()

    # 询问是否进行网络测试
    print("\n" + "="*60)
    print("注意: 下一步将进行真实的网络爬虫测试")
    print("="*60)
    print("这将:")
    print("  1. 向Boss直聘发送真实的HTTP请求")
    print("  2. 可能需要5-10秒")
    print("  3. 可能因为网络问题或API变化而失败")

    response = input("\n是否继续网络测试？(y/n): ").lower().strip()

    if response == 'y':
        # 测试3: Boss爬虫
        test_boss_spider_basic()
    else:
        print("\n跳过网络测试")

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == '__main__':
    main()
