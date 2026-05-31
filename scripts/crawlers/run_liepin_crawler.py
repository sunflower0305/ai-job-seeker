"""
猎聘网爬虫运行脚本
支持命令行参数配置
"""

from _bootstrap import PROJECT_ROOT

import sys
import argparse

from crawler.liepin_spider import LiepinSpider
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/liepin_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='猎聘网职位数据爬虫')
    parser.add_argument('--cities', nargs='+', default=['北京', '上海', '深圳', '杭州'],
                        help='要爬取的城市列表')
    parser.add_argument('--keywords', nargs='+', default=['Python', 'Java', 'Web前端', '数据分析'],
                        help='要爬取的职位关键词')
    parser.add_argument('--pages', type=int, default=3,
                        help='每个关键词爬取的页数')
    parser.add_argument('--headless', action='store_true',
                        help='使用无头模式（不显示浏览器界面）')

    args = parser.parse_args()

    # 城市代码映射
    city_map = {
        '北京': '010',
        '上海': '020',
        '广州': '030',
        '深圳': '040',
        '杭州': '050',
        '成都': '280',
        '武汉': '170',
        '南京': '070',
        '西安': '260',
        '重庆': '310',
    }

    # 转换城市列表
    cities_with_codes = [(city_map.get(city, '010'), city) for city in args.cities]

    print("="*60)
    print("猎聘网职位数据爬虫")
    print("="*60)
    print(f"目标城市: {', '.join(args.cities)}")
    print(f"关键词: {', '.join(args.keywords)}")
    print(f"每个关键词爬取: {args.pages} 页")
    print(f"浏览器模式: {'无头' if args.headless else '有头'}")
    print("="*60)

    # 创建爬虫实例
    spider = LiepinSpider(headless=args.headless)

    # 开始爬取
    spider.crawl_all(
        cities=cities_with_codes,
        keywords=args.keywords,
        max_pages=args.pages
    )

    # 保存数据
    if spider.jobs_data:
        spider.save_to_json()

        # 显示统计信息
        stats = spider.get_statistics()
        print("\n" + "="*60)
        print("爬取统计")
        print("="*60)
        print(f"总职位数: {stats['total']}")
        print(f"\n城市分布:")
        for city, count in stats['cities'].items():
            print(f"  {city}: {count} 条")

        # 显示薪资范围
        salaries = [j for j in spider.jobs_data if j.get('salary_min')]
        if salaries:
            avg_min = sum(j['salary_min'] for j in salaries) / len(salaries)
            avg_max = sum(j['salary_max'] for j in salaries) / len(salaries)
            print(f"\n平均薪资范围: {avg_min/1000:.1f}K - {avg_max/1000:.1f}K")

    else:
        print("\n未获取到任何数据")


if __name__ == '__main__':
    main()
