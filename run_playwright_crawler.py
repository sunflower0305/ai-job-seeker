"""
运行Playwright爬虫
直接爬取真实数据
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.boss_playwright_spider import BossPlaywrightSpider, PLAYWRIGHT_AVAILABLE


def main():
    """主函数"""
    print("\n" + "="*60)
    print("Boss直聘爬虫 - Playwright版本")
    print("="*60)

    if not PLAYWRIGHT_AVAILABLE:
        print("\n✗ Playwright未正确安装或导入失败")
        print("\n请检查安装:")
        print("  1. pip install playwright")
        print("  2. playwright install chromium")
        return

    print("\n✓ Playwright已就绪")
    print("\n爬取配置:")
    print("  - 目标网站: Boss直聘")
    print("  - 城市: 北京")
    print("  - 关键词: Python")
    print("  - 页数: 2页")
    print("  - 浏览器模式: 有头模式 (可以看到浏览器操作)")
    print("\n说明:")
    print("  - 浏览器将自动打开并进行操作")
    print("  - 模拟真人行为（滚动、延时等）")
    print("  - 如遇验证码会暂停，请手动完成后按回车")
    print("="*60)

    print("\n开始爬取...")
    print("（浏览器启动中，请稍候...）\n")

    try:
        # 创建爬虫实例
        # headless=False 可以看到浏览器操作过程
        spider = BossPlaywrightSpider(headless=False)

        # 爬取数据
        # 先测试少量数据
        spider.crawl_all(
            cities=['北京'],
            keywords=['Python'],
            max_pages=2  # 每个关键词爬2页
        )

        # 检查结果
        if spider.jobs_data:
            print("\n" + "="*60)
            print(f"✓ 爬取成功！共获取 {len(spider.jobs_data)} 条数据")
            print("="*60)

            # 保存数据
            filename = 'data/raw/boss_playwright_jobs.json'
            spider.save_to_json(filename)

            # 显示前5条数据样例
            print("\n【数据样例】前5条职位：\n")
            for i, job in enumerate(spider.jobs_data[:5], 1):
                print(f"职位 {i}:")
                print(f"  职位名称: {job['job_title']}")
                print(f"  公司名称: {job['company_name']}")

                salary_min = job.get('salary_min')
                salary_max = job.get('salary_max')
                if salary_min and salary_max:
                    print(f"  薪资范围: {salary_min}-{salary_max} 元/月")
                else:
                    print(f"  薪资范围: 面议")

                print(f"  工作城市: {job['city']}")
                print(f"  工作经验: {job['experience']}")
                print(f"  学历要求: {job['education']}")
                print(f"  公司规模: {job['company_size']}")
                print(f"  所属行业: {job['industry']}")

                if job.get('welfare'):
                    print(f"  福利待遇: {job['welfare'][:50]}...")

                print("-" * 60)

            # 统计信息
            stats = spider.get_statistics()
            print(f"\n【统计信息】")
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
                print(f"  平均薪资: {int(sum(salaries) / len(salaries)):,} 元/月")
                print(f"  最高薪资: {int(max(salaries)):,} 元/月")
                print(f"  最低薪资: {int(min(salaries)):,} 元/月")

            print("\n" + "="*60)
            print("爬取完成！")
            print("="*60)
            print(f"\n数据已保存到: {filename}")
            print("\n下一步建议:")
            print("  1. 查看数据文件检查质量")
            print("  2. 继续爬取更多城市/职位")
            print("  3. 进行数据清洗处理")

        else:
            print("\n" + "="*60)
            print("✗ 未获取到数据")
            print("="*60)
            print("\n可能原因:")
            print("  1. 网站触发了验证码（请检查浏览器窗口）")
            print("  2. 页面结构已更新（需要更新选择器）")
            print("  3. 网络连接问题")
            print("\n建议:")
            print("  - 检查浏览器窗口是否有验证码")
            print("  - 尝试减少爬取频率")
            print("  - 检查网络连接")

    except KeyboardInterrupt:
        print("\n\n用户中断爬取")
        print("已爬取数据将被保存...")
        if 'spider' in locals() and spider.jobs_data:
            spider.save_to_json('data/raw/boss_playwright_jobs_partial.json')
            print(f"✓ 已保存 {len(spider.jobs_data)} 条数据")

    except Exception as e:
        print(f"\n✗ 爬取过程出现异常: {e}")
        import traceback
        traceback.print_exc()

        # 尝试保存已爬取的数据
        if 'spider' in locals() and spider.jobs_data:
            print("\n尝试保存已爬取的数据...")
            spider.save_to_json('data/raw/boss_playwright_jobs_error.json')
            print(f"✓ 已保存 {len(spider.jobs_data)} 条数据")

    print("\n" + "="*60)
    print("程序结束")
    print("="*60)


if __name__ == '__main__':
    main()
