"""
Boss直聘爬虫
爬取Boss直聘网站的职位数据
"""

import requests
import json
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from typing import List, Dict
from .utils import spider_utils
from config.config import TARGET_CITIES, TARGET_JOBS, SPIDER_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BossSpider:
    """Boss直聘爬虫类"""

    def __init__(self):
        self.base_url = "https://www.zhipin.com"
        self.search_url = "https://www.zhipin.com/wapi/zpgeek/search/joblist.json"
        self.session = requests.Session()
        self.jobs_data = []

    def search_jobs(self, city: str, keyword: str, page: int = 1) -> Dict:
        """
        搜索职位

        Args:
            city: 城市名称
            keyword: 职位关键词
            page: 页码

        Returns:
            职位列表数据
        """
        params = {
            'scene': 1,
            'query': keyword,
            'city': self._get_city_code(city),
            'experience': '',
            'degree': '',
            'industry': '',
            'scale': '',
            'stage': '',
            'position': '',
            'jobType': '',
            'salary': '',
            'multiBusinessDistrict': '',
            'page': page,
            'pageSize': 30
        }

        headers = spider_utils.get_random_headers()
        headers.update({
            'Referer': 'https://www.zhipin.com/web/geek/job',
            'Accept': 'application/json, text/plain, */*',
        })

        try:
            spider_utils.random_delay()
            response = self.session.get(
                self.search_url,
                params=params,
                headers=headers,
                timeout=SPIDER_CONFIG['timeout']
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    logger.info(f"✓ 成功获取 {city} - {keyword} 第{page}页数据")
                    return data.get('zpData', {})
                else:
                    logger.warning(f"✗ API返回错误: {data.get('message')}")
            else:
                logger.error(f"✗ 请求失败，状态码: {response.status_code}")

        except Exception as e:
            logger.error(f"✗ 请求异常: {e}")

        return {}

    def parse_job_list(self, data: Dict) -> List[Dict]:
        """
        解析职位列表数据

        Args:
            data: API返回的数据

        Returns:
            解析后的职位列表
        """
        jobs = []
        job_list = data.get('jobList', [])

        for item in job_list:
            try:
                job = self._parse_job_item(item)
                jobs.append(job)
            except Exception as e:
                logger.error(f"✗ 解析职位数据失败: {e}")

        return jobs

    def _parse_job_item(self, item: Dict) -> Dict:
        """
        解析单个职位数据

        Args:
            item: 职位原始数据

        Returns:
            解析后的职位字典
        """
        # 解析薪资
        salary_desc = item.get('salaryDesc', '')
        min_salary, max_salary, salary_months = spider_utils.parse_salary(salary_desc)

        # 提取职位标签
        job_labels = item.get('jobLabels', [])
        skills = item.get('skills', [])
        all_tags = job_labels + skills

        job = {
            'job_title': item.get('jobName', ''),
            'company_name': item.get('brandName', ''),
            'salary_min': min_salary,
            'salary_max': max_salary,
            'salary_months': salary_months,
            'city': item.get('cityName', ''),
            'experience': spider_utils.standardize_experience(item.get('jobExperience', '')),
            'education': spider_utils.standardize_education(item.get('jobDegree', '')),
            'company_size': item.get('brandScaleName', ''),
            'company_type': item.get('brandStageName', ''),
            'industry': item.get('brandIndustry', ''),
            'job_description': '',  # 需要详情页获取
            'job_tags': ','.join(all_tags) if all_tags else '',
            'welfare': ','.join(item.get('welfareList', [])),
            'source': 'Boss直聘',
            'url': f"{self.base_url}/job_detail/{item.get('encryptJobId', '')}.html",
            'publish_time': None,
            'crawl_time': datetime.now()
        }

        return job

    def crawl_by_city_and_keyword(self, city: str, keyword: str, max_pages: int = 3):
        """
        爬取指定城市和关键词的职位

        Args:
            city: 城市名称
            keyword: 职位关键词
            max_pages: 最大爬取页数
        """
        logger.info(f"开始爬取: {city} - {keyword}")

        for page in range(1, max_pages + 1):
            data = self.search_jobs(city, keyword, page)

            if not data:
                logger.warning(f"第{page}页无数据，停止爬取")
                break

            jobs = self.parse_job_list(data)
            self.jobs_data.extend(jobs)

            logger.info(f"第{page}页获取到 {len(jobs)} 条职位数据")

            # 检查是否还有下一页
            if not data.get('hasMore', False):
                logger.info("已到最后一页")
                break

    def crawl_all(self, cities: List[str] = None, keywords: List[str] = None, max_pages: int = 3):
        """
        批量爬取多个城市和关键词的职位

        Args:
            cities: 城市列表
            keywords: 关键词列表
            max_pages: 每个关键词最大爬取页数
        """
        cities = cities or TARGET_CITIES
        keywords = keywords or TARGET_JOBS

        logger.info(f"="*60)
        logger.info(f"开始批量爬取任务")
        logger.info(f"目标城市: {', '.join(cities)}")
        logger.info(f"职位关键词: {', '.join(keywords)}")
        logger.info(f"="*60)

        total_jobs = 0

        for city in cities:
            for keyword in keywords:
                try:
                    before_count = len(self.jobs_data)
                    self.crawl_by_city_and_keyword(city, keyword, max_pages)
                    after_count = len(self.jobs_data)
                    current_count = after_count - before_count

                    total_jobs += current_count
                    logger.info(f"✓ {city} - {keyword}: 获取 {current_count} 条数据")

                except Exception as e:
                    logger.error(f"✗ {city} - {keyword} 爬取失败: {e}")

                # 每个关键词之间延时
                time.sleep(random.uniform(2, 5))

        logger.info(f"="*60)
        logger.info(f"爬取完成！共获取 {total_jobs} 条职位数据")
        logger.info(f"="*60)

    def save_to_json(self, filename: str = None):
        """
        保存数据到JSON文件

        Args:
            filename: 文件名
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/raw/boss_jobs_{timestamp}.json"

        try:
            # 转换datetime为字符串
            data_to_save = []
            for job in self.jobs_data:
                job_copy = job.copy()
                if isinstance(job_copy.get('crawl_time'), datetime):
                    job_copy['crawl_time'] = job_copy['crawl_time'].strftime('%Y-%m-%d %H:%M:%S')
                if isinstance(job_copy.get('publish_time'), datetime):
                    job_copy['publish_time'] = job_copy['publish_time'].strftime('%Y-%m-%d %H:%M:%S')
                data_to_save.append(job_copy)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ 数据已保存到: {filename}")
            logger.info(f"✓ 共保存 {len(data_to_save)} 条数据")

        except Exception as e:
            logger.error(f"✗ 保存文件失败: {e}")

    def _get_city_code(self, city_name: str) -> str:
        """
        获取城市代码（Boss直聘的城市编码）

        Args:
            city_name: 城市名称

        Returns:
            城市代码
        """
        # Boss直聘主要城市代码映射
        city_codes = {
            '北京': '101010100',
            '上海': '101020100',
            '广州': '101280100',
            '深圳': '101280600',
            '杭州': '101210100',
            '成都': '101270100',
            '武汉': '101200100',
            '南京': '101190100',
            '西安': '101110100',
            '重庆': '101040100',
            '天津': '101030100',
            '苏州': '101190400',
            '郑州': '101180100',
            '长沙': '101250100',
            '东莞': '101281600',
        }

        return city_codes.get(city_name, '101010100')  # 默认返回北京

    def get_statistics(self) -> Dict:
        """
        获取爬取数据的统计信息

        Returns:
            统计信息字典
        """
        if not self.jobs_data:
            return {}

        cities = {}
        jobs = {}

        for job in self.jobs_data:
            city = job.get('city', '未知')
            job_title = job.get('job_title', '未知')

            cities[city] = cities.get(city, 0) + 1
            jobs[job_title] = jobs.get(job_title, 0) + 1

        return {
            'total': len(self.jobs_data),
            'cities': cities,
            'jobs': jobs,
        }


def main():
    """主函数"""
    spider = BossSpider()

    # 方式1：爬取指定城市和关键词
    # spider.crawl_by_city_and_keyword('北京', 'Python', max_pages=2)

    # 方式2：批量爬取
    spider.crawl_all(
        cities=['北京', '上海', '深圳', '杭州'],
        keywords=['Python', 'Java', 'Web前端', '数据分析'],
        max_pages=2
    )

    # 保存数据
    if spider.jobs_data:
        spider.save_to_json()

        # 显示统计信息
        stats = spider.get_statistics()
        print(f"\n统计信息:")
        print(f"总职位数: {stats['total']}")
        print(f"城市分布: {stats['cities']}")


if __name__ == '__main__':
    main()
