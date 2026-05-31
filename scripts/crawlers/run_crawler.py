"""
爬虫主程序
统一管理多个招聘网站的爬虫
"""

from _bootstrap import PROJECT_ROOT

import argparse
import json
from datetime import datetime
from crawler.boss_spider import BossSpider
from crawler.zhilian_spider import ZhilianSpider
from config.config import TARGET_CITIES, TARGET_JOBS


def merge_job_data(spider_list):
    """
    合并多个爬虫的数据

    Args:
        spider_list: 爬虫实例列表

    Returns:
        合并后的职位数据列表
    """
    all_jobs = []

    for spider in spider_list:
        all_jobs.extend(spider.jobs_data)

    return all_jobs


def save_merged_data(jobs_data, filename=None):
    """
    保存合并后的数据

    Args:
        jobs_data: 职位数据列表
        filename: 保存文件名
    """
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/raw/all_jobs_{timestamp}.json"

    try:
        # 转换datetime为字符串
        data_to_save = []
        for job in jobs_data:
            job_copy = job.copy()
            if isinstance(job_copy.get('crawl_time'), datetime):
                job_copy['crawl_time'] = job_copy['crawl_time'].strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(job_copy.get('publish_time'), datetime):
                job_copy['publish_time'] = job_copy['publish_time'].strftime('%Y-%m-%d %H:%M:%S')
            data_to_save.append(job_copy)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 合并数据已保存到: {filename}")
        print(f"✓ 共保存 {len(data_to_save)} 条数据")

    except Exception as e:
        print(f"✗ 保存文件失败: {e}")


def print_statistics(jobs_data):
    """
    打印数据统计信息

    Args:
        jobs_data: 职位数据列表
    """
    if not jobs_data:
        print("暂无数据")
        return

    # 统计来源
    sources = {}
    cities = {}
    for job in jobs_data:
        source = job.get('source', '未知')
        city = job.get('city', '未知')

        sources[source] = sources.get(source, 0) + 1
        cities[city] = cities.get(city, 0) + 1

    print("\n" + "="*60)
    print("数据统计")
    print("="*60)
    print(f"总职位数: {len(jobs_data)}")
    print(f"\n数据来源分布:")
    for source, count in sources.items():
        print(f"  - {source}: {count} 条")

    print(f"\n城市分布:")
    for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {city}: {count} 条")
    print("="*60)


def run_boss_spider(cities, keywords, max_pages):
    """运行Boss直聘爬虫"""
    print("\n【Boss直聘爬虫】")
    spider = BossSpider()
    spider.crawl_all(cities, keywords, max_pages)
    spider.save_to_json()
    return spider


def run_zhilian_spider(cities, keywords, max_pages):
    """运行智联招聘爬虫"""
    print("\n【智联招聘爬虫】")
    spider = ZhilianSpider()
    spider.crawl_all(cities, keywords, max_pages)
    spider.save_to_json()
    return spider


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='招聘数据爬虫程序')

    parser.add_argument(
        '--spider',
        type=str,
        choices=['boss', 'zhilian', 'all'],
        default='all',
        help='选择爬虫: boss(Boss直聘), zhilian(智联招聘), all(全部)'
    )

    parser.add_argument(
        '--cities',
        type=str,
        nargs='+',
        default=None,
        help='目标城市列表，如: --cities 北京 上海 深圳'
    )

    parser.add_argument(
        '--keywords',
        type=str,
        nargs='+',
        default=None,
        help='职位关键词列表，如: --keywords Python Java'
    )

    parser.add_argument(
        '--pages',
        type=int,
        default=2,
        help='每个关键词爬取的最大页数，默认2页'
    )

    args = parser.parse_args()

    # 使用配置文件中的默认值或命令行参数
    cities = args.cities or TARGET_CITIES[:4]  # 默认取前4个城市
    keywords = args.keywords or TARGET_JOBS[:4]  # 默认取前4个关键词
    max_pages = args.pages

    print("="*60)
    print("招聘数据爬虫程序")
    print("="*60)
    print(f"爬虫类型: {args.spider}")
    print(f"目标城市: {', '.join(cities)}")
    print(f"职位关键词: {', '.join(keywords)}")
    print(f"每个关键词最大页数: {max_pages}")
    print("="*60)

    spider_list = []

    # 运行爬虫
    if args.spider in ['boss', 'all']:
        spider_list.append(run_boss_spider(cities, keywords, max_pages))

    if args.spider in ['zhilian', 'all']:
        spider_list.append(run_zhilian_spider(cities, keywords, max_pages))

    # 合并数据
    if len(spider_list) > 1:
        all_jobs = merge_job_data(spider_list)
        save_merged_data(all_jobs)
        print_statistics(all_jobs)
    elif len(spider_list) == 1:
        print_statistics(spider_list[0].jobs_data)

    print("\n✓ 爬虫任务全部完成！")


if __name__ == '__main__':
    main()
