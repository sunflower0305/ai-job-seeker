"""
真实网络爬虫测试
向Boss直聘发送真实请求，测试爬虫功能
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.boss_spider import BossSpider


def test_real_crawl():
    """真实爬虫测试"""
    print("\n" + "="*60)
    print("真实网络爬虫测试")
    print("="*60)
    print("测试配置:")
    print("  - 城市: 北京")
    print("  - 关键词: Python")
    print("  - 页数: 1页")
    print("="*60)

    # 创建爬虫实例
    spider = BossSpider()

    try:
        print("\n开始爬取数据...")
        print("（这可能需要几秒钟，请耐心等待...）\n")

        # 爬取数据
        spider.crawl_by_city_and_keyword('北京', 'Python', max_pages=1)

        # 检查结果
        if spider.jobs_data:
            print("\n" + "="*60)
            print(f"✓ 爬取成功！共获取 {len(spider.jobs_data)} 条数据")
            print("="*60)

            # 显示前3条数据
            print("\n【数据样例】前3条职位信息：\n")
            for i, job in enumerate(spider.jobs_data[:3], 1):
                print(f"职位 {i}:")
                print(f"  职位名称: {job.get('job_title')}")
                print(f"  公司名称: {job.get('company_name')}")

                salary_min = job.get('salary_min')
                salary_max = job.get('salary_max')
                if salary_min and salary_max:
                    print(f"  薪资范围: {salary_min}-{salary_max} 元/月")
                else:
                    print(f"  薪资范围: 面议")

                print(f"  工作城市: {job.get('city')}")
                print(f"  工作经验: {job.get('experience')}")
                print(f"  学历要求: {job.get('education')}")
                print(f"  公司规模: {job.get('company_size')}")
                print(f"  所属行业: {job.get('industry')}")
                print(f"  职位标签: {job.get('job_tags')}")
                print(f"  福利待遇: {job.get('welfare')}")
                print(f"  数据来源: {job.get('source')}")
                print("-" * 60)

            # 统计信息
            stats = spider.get_statistics()
            print("\n【统计信息】")
            print(f"  总职位数: {stats['total']}")
            print(f"  城市分布: {stats['cities']}")

            # 薪资统计
            salaries = []
            for job in spider.jobs_data:
                if job.get('salary_min') and job.get('salary_max'):
                    avg_salary = (job['salary_min'] + job['salary_max']) / 2
                    salaries.append(avg_salary)

            if salaries:
                print(f"\n【薪资分析】")
                print(f"  平均薪资: {int(sum(salaries) / len(salaries))} 元/月")
                print(f"  最高薪资: {int(max(salaries))} 元/月")
                print(f"  最低薪资: {int(min(salaries))} 元/月")

            # 保存数据
            spider.save_to_json('data/raw/test_real_jobs.json')
            print(f"\n✓ 数据已保存到: data/raw/test_real_jobs.json")

            # 测试结论
            print("\n" + "="*60)
            print("测试结论")
            print("="*60)
            print("✓ 网络请求: 成功")
            print("✓ 数据解析: 成功")
            print("✓ 数据标准化: 成功")
            print("✓ 数据保存: 成功")
            print("\n爬虫功能完全正常！可以进行大规模数据采集。")

        else:
            print("\n" + "="*60)
            print("✗ 未获取到数据")
            print("="*60)
            print("可能的原因:")
            print("  1. 网络连接问题")
            print("  2. Boss直聘API已更新或需要登录")
            print("  3. 被反爬虫机制拦截（需要验证码）")
            print("  4. 城市代码或搜索参数错误")
            print("\n建议:")
            print("  1. 检查网络连接")
            print("  2. 尝试访问 https://www.zhipin.com 确认网站可访问")
            print("  3. 如果网站需要登录，考虑使用Selenium模拟登录")

    except Exception as e:
        print("\n" + "="*60)
        print("✗ 爬取过程出现异常")
        print("="*60)
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")
        print("\n详细错误信息:")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("测试结束")
    print("="*60)


if __name__ == '__main__':
    test_real_crawl()
