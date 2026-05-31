"""
测试Playwright爬虫
"""

from _bootstrap import PROJECT_ROOT

import sys
import os

# 将项目根目录添加到Python路径

from crawler.boss_playwright_spider import BossPlaywrightSpider, PLAYWRIGHT_AVAILABLE


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("Playwright爬虫测试")
    print("="*60)

    if not PLAYWRIGHT_AVAILABLE:
        print("\n✗ Playwright未安装或未正确配置")
        print("\n请按以下步骤安装:")
        print("  1. pip install playwright")
        print("  2. playwright install chromium")
        return

    print("\n✓ Playwright已安装")
    print("\n测试配置:")
    print("  - 目标网站: Boss直聘")
    print("  - 城市: 北京")
    print("  - 关键词: Python")
    print("  - 页数: 1页")
    print("  - 浏览器模式: 无头模式 (headless=True)")
    print("\n说明:")
    print("  - 使用浏览器自动化，可以绕过简单的反爬虫")
    print("  - 模拟真人操作（滚动、延时等）")
    print("  - 如果遇到验证码，程序会暂停等待手动完成")
    print("="*60)

    response = input("\n是否开始测试？(y/n): ").lower().strip()

    if response != 'y':
        print("\n测试已取消")
        return

    print("\n开始测试...")
    print("（浏览器启动中...）\n")

    try:
        # 创建爬虫实例（headless=True不显示浏览器窗口）
        spider = BossPlaywrightSpider(headless=True)

        # 爬取数据
        spider.crawl_all(
            cities=['北京'],
            keywords=['Python'],
            max_pages=1
        )

        # 检查结果
        if spider.jobs_data:
            print("\n" + "="*60)
            print(f"✓ 测试成功！共获取 {len(spider.jobs_data)} 条数据")
            print("="*60)

            # 保存数据
            spider.save_to_json('data/raw/test_playwright_jobs.json')

            # 显示样例
            print("\n【数据样例】前3条：\n")
            for i, job in enumerate(spider.jobs_data[:3], 1):
                print(f"职位 {i}:")
                print(f"  职位: {job['job_title']}")
                print(f"  公司: {job['company_name']}")
                print(f"  薪资: {job['salary_min']}-{job['salary_max']} 元/月")
                print(f"  城市: {job['city']}")
                print(f"  经验: {job['experience']}")
                print(f"  学历: {job['education']}")
                print("-" * 60)

            # 统计信息
            stats = spider.get_statistics()
            print(f"\n统计信息:")
            print(f"  总数: {stats['total']}")
            print(f"  城市分布: {stats['cities']}")

            print("\n" + "="*60)
            print("测试结论")
            print("="*60)
            print("✓ Playwright爬虫功能正常")
            print("✓ 可以成功绕过基本的反爬虫机制")
            print("✓ 数据解析和保存功能正常")
            print("\n建议:")
            print("  - 实际使用时可以设置 headless=False 观察浏览器行为")
            print("  - 适当增加延时避免触发更严格的反爬虫")
            print("  - 如遇到滑块验证码，需要手动处理")

        else:
            print("\n" + "="*60)
            print("✗ 未获取到数据")
            print("="*60)
            print("可能原因:")
            print("  1. 网站触发了验证码")
            print("  2. 页面结构已更新")
            print("  3. 网络连接问题")

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("测试结束")
    print("="*60)


if __name__ == '__main__':
    main()
