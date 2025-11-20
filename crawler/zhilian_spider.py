"""
智联招聘爬虫
爬取智联招聘网站的职位数据
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


class ZhilianSpider:
    """智联招聘爬虫类"""

    def __init__(self):
        self.base_url = "https://www.zhaopin.com"
        self.search_url = "https://fe-api.zhaopin.com/c/i/sou"
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
            'pageIndex': page,
            'pageSize': 60,
            'cityId': self._get_city_code(city),
            'workExperience': -1,
            'education': -1,
            'companyType': -1,
            'employmentType': -1,
            'jobWelfareTag': -1,
            'kw': keyword,
            'kt': 3
        }

        headers = spider_utils.get_random_headers()
        headers.update({
            'Referer': 'https://www.zhaopin.com/',
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
                if data.get('code') == 200:
                    logger.info(f"✓ 成功获取 {city} - {keyword} 第{page}页数据")
                    return data.get('data', {})
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
        job_list = data.get('results', [])

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
        salary_desc = item.get('salary', '')
        min_salary, max_salary, salary_months = spider_utils.parse_salary(salary_desc)

        # 提取职位标签
        welfare_list = item.get('welfare', '').split(',') if item.get('welfare') else []

        # 解析城市信息
        city_info = item.get('city', {})
        city_name = city_info.get('display', '') if isinstance(city_info, dict) else ''

        # 解析公司信息
        company = item.get('company', {})
        company_name = company.get('name', '') if isinstance(company, dict) else ''
        company_size = company.get('size', {}).get('name', '') if isinstance(company, dict) else ''
        company_type = company.get('type', {}).get('name', '') if isinstance(company, dict) else ''
        industry = company.get('industry', {}).get('name', '') if isinstance(company, dict) else ''

        job = {
            'job_title': item.get('jobName', ''),
            'company_name': company_name,
            'salary_min': min_salary,
            'salary_max': max_salary,
            'salary_months': salary_months,
            'city': spider_utils.standardize_city(city_name),
            'experience': spider_utils.standardize_experience(item.get('workingExp', {}).get('name', '')),
            'education': spider_utils.standardize_education(item.get('eduLevel', {}).get('name', '')),
            'company_size': company_size,
            'company_type': company_type,
            'industry': industry,
            'job_description': item.get('highlight', ''),
            'job_tags': '',
            'welfare': ','.join(welfare_list),
            'source': '智联招聘',
            'url': item.get('positionURL', ''),
            'publish_time': self._parse_time(item.get('updateDate', '')),
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

            # 智联招聘检查总数
            total_count = data.get('numFound', 0)
            if len(self.jobs_data) >= total_count:
                logger.info("已获取所有数据")
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
            filename = f"data/raw/zhilian_jobs_{timestamp}.json"

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
        获取城市代码（智联招聘的城市编码）

        Args:
            city_name: 城市名称

        Returns:
            城市代码
        """
        # 智联招聘主要城市代码映射
        city_codes = {
            '北京': '530',
            '上海': '538',
            '广州': '763',
            '深圳': '765',
            '杭州': '653',
            '成都': '801',
            '武汉': '736',
            '南京': '635',
            '西安': '854',
            '重庆': '854',
            '天津': '531',
            '苏州': '636',
            '郑州': '719',
            '长沙': '749',
            '东莞': '781',
        }

        return city_codes.get(city_name, '530')  # 默认返回北京

    def _parse_time(self, time_str: str) -> datetime:
        """
        解析时间字符串

        Args:
            time_str: 时间字符串

        Returns:
            datetime对象
        """
        if not time_str:
            return None

        try:
            # 智联招聘时间格式：2024-01-15
            return datetime.strptime(time_str, '%Y-%m-%d')
        except:
            return None

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
    spider = ZhilianSpider()

    # 批量爬取
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
