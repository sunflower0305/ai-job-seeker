"""
运行智能爬虫
可自定义爬取参数
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.boss_smart_spider import BossSmartSpider, PLAYWRIGHT_AVAILABLE


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Boss直聘智能爬虫')

    parser.add_argument(
        '--cities',
        nargs='+',
        default=['北京', '上海'],
        help='城市列表，如: --cities 北京 上海 深圳'
    )

    parser.add_argument(
        '--keywords',
        nargs='+',
        default=['Python'],
        help='关键词列表，如: --keywords Python Java'
    )

    parser.add_argument(
        '--per-keyword',
        type=int,
        default=50,
        help='每个关键词最大爬取数，默认50'
    )

    parser.add_argument(
        '--total',
        type=int,
        default=200,
        help='总计最大爬取数，默认200'
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        help='无头模式（不显示浏览器）'
    )

    parser.add_argument(
        '--cookie-file',
        default='data/cookies.json',
        help='Cookie保存文件路径'
    )

    args = parser.parse_args()

    if not PLAYWRIGHT_AVAILABLE:
        print("\n✗ Playwright未安装")
        print("\n请执行:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return

    print("\n" + "="*60)
    print("Boss直聘智能爬虫 - 配置")
    print("="*60)
    print(f"城市: {', '.join(args.cities)}")
    print(f"关键词: {', '.join(args.keywords)}")
    print(f"每个关键词最多: {args.per_keyword} 条")
    print(f"总计最多: {args.total} 条")
    print(f"浏览器模式: {'无头' if args.headless else '有头（可见）'}")
    print(f"Cookie文件: {args.cookie_file}")
    print("="*60)

    print("\n说明:")
    print("  1. 首次运行需要手动登录Boss直聘")
    print("  2. 登录后Cookie会自动保存，下次自动登录")
    print("  3. 如遇验证码，会暂停等待手动完成")
    print("  4. 爬取速度已优化，避免触发反爬虫")
    print("  5. 可随时Ctrl+C中断，已爬取数据会保存")

    response = input("\n是否开始爬取？(y/n): ").lower().strip()

    if response != 'y':
        print("\n已取消")
        return

    try:
        # 创建爬虫
        spider = BossSmartSpider(
            headless=args.headless,
            cookie_file=args.cookie_file
        )

        # 执行爬取
        spider.crawl_controlled(
            cities=args.cities,
            keywords=args.keywords,
            max_jobs_per_keyword=args.per_keyword,
            max_total=args.total
        )

        # 保存数据
        if spider.jobs_data:
            filename = spider.save_to_json()

            # 统计信息
            spider.print_stats()

            # 样例展示
            print("\n" + "="*60)
            print("数据样例（前5条）")
            print("="*60)
            for i, job in enumerate(spider.jobs_data[:5], 1):
                print(f"\n{i}. {job['job_title']}")
                print(f"   公司: {job['company_name']}")
                print(f"   薪资: {job['salary_min']}-{job['salary_max']} 元/月")
                print(f"   城市: {job['city']}")
                print(f"   要求: {job['experience']} | {job['education']}")
                print(f"   行业: {job['industry']}")

            print("\n" + "="*60)
            print("✓ 爬取完成！")
            print("="*60)
            print(f"\n数据已保存到: {filename}")
            print(f"共获取 {len(spider.jobs_data)} 条职位数据")

            print("\n下一步:")
            print("  - 可以继续爬取更多数据")
            print("  - 或进行数据清洗和分析")

        else:
            print("\n未获取到数据")

    except KeyboardInterrupt:
        print("\n\n用户中断")
        if 'spider' in locals() and spider.jobs_data:
            print(f"保存已爬取的 {len(spider.jobs_data)} 条数据...")
            spider.save_to_json('data/raw/boss_smart_interrupted.json')
            print("✓ 数据已保存")

    except Exception as e:
        print(f"\n✗ 出现异常: {e}")
        import traceback
        traceback.print_exc()

        if 'spider' in locals() and spider.jobs_data:
            print(f"\n保存已爬取的 {len(spider.jobs_data)} 条数据...")
            spider.save_to_json('data/raw/boss_smart_error.json')


if __name__ == '__main__':
    main()
