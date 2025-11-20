"""
猎聘网爬虫
使用Playwright爬取猎聘网职位数据（无需登录）
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright
from typing import List, Dict
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LiepinSpider:
    """猎聘网爬虫类"""

    def __init__(self, headless=True):
        """
        初始化爬虫

        Args:
            headless: 是否使用无头模式
        """
        self.jobs_data = []
        self.headless = headless

    async def crawl_jobs(self, keyword="Python", city="010", max_pages=3):
        """
        爬取职位数据

        Args:
            keyword: 搜索关键词
            city: 城市代码 (010=北京, 020=上海, 030=广州, 040=深圳, 050=杭州)
            max_pages: 最大页数
        """
        async with async_playwright() as p:
            logger.info(f"启动浏览器（{'无头' if self.headless else '有头'}模式）...")
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            try:
                for page_num in range(max_pages):
                    # 猎聘的搜索URL
                    search_url = f"https://www.liepin.com/zhaopin/?key={keyword}&dq={city}&currentPage={page_num}"
                    logger.info(f"正在爬取第 {page_num + 1} 页...")

                    try:
                        await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                        await asyncio.sleep(3)

                        # 等待职位列表加载
                        await page.wait_for_selector('.job-list-box', timeout=10000)

                        # 滚动页面，确保所有内容加载
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await asyncio.sleep(2)

                        # 提取职位信息
                        jobs = await self._extract_jobs_from_page(page)
                        logger.info(f"第 {page_num + 1} 页获取到 {len(jobs)} 条职位")

                        if jobs:
                            self.jobs_data.extend(jobs)
                        else:
                            logger.warning(f"第 {page_num + 1} 页未获取到数据")

                        # 页面之间延迟
                        await asyncio.sleep(2)

                    except Exception as e:
                        logger.error(f"第 {page_num + 1} 页爬取失败: {e}")
                        continue

            except Exception as e:
                logger.error(f"爬取过程出错: {e}")

            finally:
                await browser.close()

        # 去重
        self._remove_duplicates()
        logger.info(f"爬取完成，共获取 {len(self.jobs_data)} 条有效职位数据")

    async def _extract_jobs_from_page(self, page):
        """从页面提取职位信息"""
        jobs = []

        try:
            # 使用JavaScript提取数据
            jobs_data = await page.evaluate("""
                () => {
                    const jobs = [];

                    // 尝试多种选择器
                    let jobElements = document.querySelectorAll('.job-card-box');
                    if (jobElements.length === 0) {
                        jobElements = document.querySelectorAll('[class*="job-card"]');
                    }
                    if (jobElements.length === 0) {
                        jobElements = document.querySelectorAll('.job-list-item');
                    }
                    if (jobElements.length === 0) {
                        jobElements = document.querySelectorAll('div[data-job-id]');
                    }

                    jobElements.forEach((item, index) => {
                        try {
                            // 尝试多种职位标题选择器
                            let titleEl = item.querySelector('.job-title-text') ||
                                         item.querySelector('.job-name') ||
                                         item.querySelector('[class*="job-title"]') ||
                                         item.querySelector('a[class*="title"]');

                            // 尝试多种公司名称选择器
                            let companyEl = item.querySelector('.comp-name a') ||
                                          item.querySelector('.company-name') ||
                                          item.querySelector('[class*="company"]');

                            // 尝试多种薪资选择器
                            let salaryEl = item.querySelector('.job-info .text-warning') ||
                                         item.querySelector('.salary') ||
                                         item.querySelector('[class*="salary"]');

                            const job = {
                                job_title: titleEl ? titleEl.innerText.trim() : '',
                                company_name: companyEl ? companyEl.innerText.trim() : '',
                                salary: salaryEl ? salaryEl.innerText.trim() : '',
                                url: titleEl && titleEl.href ? titleEl.href : ''
                            };

                            // 只保存有标题和公司的职位
                            if (job.job_title && job.company_name) {
                                jobs.push(job);
                            }
                        } catch (e) {
                            // 忽略解析错误
                        }
                    });

                    return jobs;
                }
            """)

            # 处理提取的数据
            for job_data in jobs_data:
                job = self._process_job_data(job_data)
                if job:
                    jobs.append(job)

        except Exception as e:
            logger.error(f"提取职位数据失败: {e}")

        return jobs

    def _process_job_data(self, raw_data):
        """处理职位数据"""
        try:
            # 解析薪资
            salary_text = raw_data.get('salary', '')
            min_salary, max_salary = self._parse_salary(salary_text)

            # 清理职位标题（移除地点信息）
            job_title = raw_data.get('job_title', '')
            # 移除【城市-区】这样的信息
            job_title = re.sub(r'【[^】]*】', '', job_title).strip()
            # 移除换行
            job_title = job_title.replace('\n', ' ').strip()

            job = {
                'job_title': job_title,
                'company_name': raw_data.get('company_name', ''),
                'salary_min': min_salary,
                'salary_max': max_salary,
                'salary_months': 12,
                'city': '北京',  # 可以从URL参数获取
                'experience': '不限',
                'education': '不限',
                'company_size': '',
                'company_type': '',
                'industry': '',
                'job_description': '',
                'job_tags': '',
                'welfare': '',
                'source': '猎聘网',
                'url': raw_data.get('url', ''),
                'publish_time': None,
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            return job
        except Exception as e:
            logger.error(f"处理职位数据失败: {e}")
            return None

    def _parse_salary(self, salary_text):
        """解析薪资"""
        if not salary_text or '面议' in salary_text:
            return None, None

        try:
            # 移除空格和逗号
            salary_text = salary_text.replace(' ', '').replace(',', '')

            # 匹配类似 "20-35K" 的格式
            if 'K' in salary_text or 'k' in salary_text:
                match = re.search(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)[Kk]', salary_text)
                if match:
                    min_salary = int(float(match.group(1)) * 1000)
                    max_salary = int(float(match.group(2)) * 1000)
                    return min_salary, max_salary

            # 匹配类似 "2-3.5万" 的格式
            elif '万' in salary_text:
                match = re.search(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)万', salary_text)
                if match:
                    min_salary = int(float(match.group(1)) * 10000)
                    max_salary = int(float(match.group(2)) * 10000)
                    return min_salary, max_salary

            return None, None

        except Exception as e:
            logger.warning(f"薪资解析失败: {salary_text}, 错误: {e}")
            return None, None

    def _remove_duplicates(self):
        """去除重复数据"""
        seen = set()
        unique_jobs = []

        for job in self.jobs_data:
            # 使用标题+公司作为唯一标识
            key = f"{job['job_title']}_{job['company_name']}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        removed = len(self.jobs_data) - len(unique_jobs)
        if removed > 0:
            logger.info(f"去除 {removed} 条重复数据")

        self.jobs_data = unique_jobs

    def crawl_by_city_and_keyword(self, city_code, city_name, keyword, max_pages=3):
        """
        爬取指定城市和关键词的职位

        Args:
            city_code: 城市代码
            city_name: 城市名称
            keyword: 职位关键词
            max_pages: 最大爬取页数
        """
        logger.info(f"开始爬取: {city_name} - {keyword}")

        asyncio.run(self.crawl_jobs(keyword=keyword, city=city_code, max_pages=max_pages))

        # 更新城市信息
        for job in self.jobs_data:
            if not job['city']:
                job['city'] = city_name

    def crawl_all(self, cities: List[tuple] = None, keywords: List[str] = None, max_pages: int = 3):
        """
        批量爬取多个城市和关键词的职位

        Args:
            cities: 城市列表 [(code, name), ...]
            keywords: 关键词列表
            max_pages: 每个关键词最大爬取页数
        """
        if cities is None:
            cities = [
                ('010', '北京'),
                ('020', '上海'),
                ('040', '深圳'),
                ('050', '杭州'),
            ]

        if keywords is None:
            keywords = ['Python', 'Java', 'Web前端', '数据分析']

        logger.info("="*60)
        logger.info("开始批量爬取任务")
        logger.info(f"目标城市: {[c[1] for c in cities]}")
        logger.info(f"职位关键词: {keywords}")
        logger.info("="*60)

        total_before = len(self.jobs_data)

        for city_code, city_name in cities:
            for keyword in keywords:
                try:
                    before_count = len(self.jobs_data)
                    self.crawl_by_city_and_keyword(city_code, city_name, keyword, max_pages)
                    after_count = len(self.jobs_data)
                    current_count = after_count - before_count

                    logger.info(f"✓ {city_name} - {keyword}: 获取 {current_count} 条数据")

                except Exception as e:
                    logger.error(f"✗ {city_name} - {keyword} 爬取失败: {e}")

        total_jobs = len(self.jobs_data) - total_before

        logger.info("="*60)
        logger.info(f"爬取完成！共获取 {total_jobs} 条职位数据")
        logger.info("="*60)

    def save_to_json(self, filename: str = None):
        """
        保存数据到JSON文件

        Args:
            filename: 文件名
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/raw/liepin_jobs_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.jobs_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ 数据已保存到: {filename}")
            logger.info(f"✓ 共保存 {len(self.jobs_data)} 条数据")

            # 显示统计信息
            valid_count = len([j for j in self.jobs_data if j['salary_min']])
            logger.info(f"✓ 其中有薪资信息的: {valid_count} 条")

        except Exception as e:
            logger.error(f"✗ 保存文件失败: {e}")

    def get_statistics(self) -> Dict:
        """
        获取爬取数据的统计信息

        Returns:
            统计信息字典
        """
        if not self.jobs_data:
            return {}

        cities = {}
        jobs_count = {}

        for job in self.jobs_data:
            city = job.get('city', '未知')
            job_title = job.get('job_title', '未知')

            cities[city] = cities.get(city, 0) + 1
            jobs_count[job_title] = jobs_count.get(job_title, 0) + 1

        return {
            'total': len(self.jobs_data),
            'cities': cities,
            'jobs': jobs_count,
        }


def main():
    """主函数"""
    spider = LiepinSpider(headless=True)

    # 批量爬取
    spider.crawl_all(
        cities=[('010', '北京'), ('020', '上海')],
        keywords=['Python', 'Java'],
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
