"""
测试智联招聘API是否可以不登录使用
"""

import sys
sys.path.insert(0, '/home/leyang/workplace/bishe')

from crawler.zhilian_spider import ZhilianSpider
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """测试智联招聘API"""
    spider = ZhilianSpider()

    print("="*60)
    print("测试智联招聘API（不登录）")
    print("="*60)

    # 测试爬取北京的Python职位，只爬2页
    spider.crawl_all(
        cities=['北京'],
        keywords=['Python'],
        max_pages=2
    )

    # 保存数据
    if spider.jobs_data:
        spider.save_to_json()

        # 显示统计
        stats = spider.get_statistics()
        print(f"\n统计信息:")
        print(f"总职位数: {stats['total']}")
    else:
        print("\n未获取到数据，可能需要登录或API已失效")

if __name__ == '__main__':
    main()
