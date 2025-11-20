"""
Boss直聘爬虫 - Playwright版本
使用浏览器自动化模拟真人操作
"""

import json
import time
import random
from datetime import datetime
from typing import List, Dict
import logging

try:
    from playwright.sync_api import sync_playwright, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("警告: Playwright未安装，请运行: pip install playwright && playwright install chromium")

from config.config import TARGET_CITIES, TARGET_JOBS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BossPlaywrightSpider:
    """Boss直聘爬虫 - Playwright版本"""

    def __init__(self, headless=True):
        """
        初始化爬虫

        Args:
            headless: 是否无头模式（True=不显示浏览器窗口）
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright未安装")

        self.headless = headless
        self.jobs_data = []
        self.playwright = None
        self.browser = None
        self.page = None

    def start_browser(self):
        """启动浏览器"""
        logger.info("正在启动浏览器...")
        self.playwright = sync_playwright().start()

        # 启动Chromium浏览器
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )

        # 创建浏览器上下文
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # 创建页面
        self.page = context.new_page()

        # 设置超时时间
        self.page.set_default_timeout(30000)

        logger.info("✓ 浏览器启动成功")

    def close_browser(self):
        """关闭浏览器"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("✓ 浏览器已关闭")

    def human_like_delay(self, min_sec=1, max_sec=3):
        """模拟人类操作延时"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def scroll_page(self):
        """模拟人类滚动页面"""
        # 随机滚动
        scroll_times = random.randint(2, 4)
        for _ in range(scroll_times):
            scroll_distance = random.randint(300, 600)
            self.page.evaluate(f'window.scrollBy(0, {scroll_distance})')
            time.sleep(random.uniform(0.5, 1.5))

    def search_jobs(self, city: str, keyword: str, page_num: int = 1):
        """
        搜索职位

        Args:
            city: 城市名称
            keyword: 职位关键词
            page_num: 页码
        """
        try:
            # 构建搜索URL
            url = f"https://www.zhipin.com/web/geek/job?query={keyword}&city={self._get_city_code(city)}&page={page_num}"

            logger.info(f"正在访问: {city} - {keyword} - 第{page_num}页")

            # 访问页面
            self.page.goto(url, wait_until='domcontentloaded')

            # 等待页面加载
            self.human_like_delay(2, 4)

            # 检查是否需要验证
            if self._check_captcha():
                logger.warning("检测到验证码，请手动完成验证...")
                # 等待用户手动完成验证
                input("完成验证后按回车继续...")

            # 等待职位列表加载
            try:
                self.page.wait_for_selector('.job-list-box', timeout=10000)
            except:
                logger.warning("职位列表加载超时")
                return []

            # 模拟人类行为：滚动页面
            self.scroll_page()

            # 等待一下
            self.human_like_delay(1, 2)

            # 解析职位列表
            jobs = self._parse_job_list()

            logger.info(f"✓ 第{page_num}页获取到 {len(jobs)} 条数据")

            return jobs

        except Exception as e:
            logger.error(f"✗ 搜索失败: {e}")
            return []

    def _check_captcha(self):
        """检查是否出现验证码"""
        try:
            # 检查常见的验证码元素
            captcha_selectors = [
                '.verify-wrap',
                '.captcha',
                '#verify-container',
            ]

            for selector in captcha_selectors:
                if self.page.query_selector(selector):
                    return True

            return False
        except:
            return False

    def _parse_job_list(self):
        """解析页面上的职位列表"""
        jobs = []

        try:
            # 获取所有职位卡片
            job_cards = self.page.query_selector_all('.job-card-wrapper')

            logger.info(f"找到 {len(job_cards)} 个职位卡片")

            for card in job_cards:
                try:
                    job = self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"解析职位卡片失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"解析职位列表失败: {e}")

        return jobs

    def _parse_job_card(self, card):
        """解析单个职位卡片"""
        try:
            # 职位名称
            job_title_elem = card.query_selector('.job-name')
            job_title = job_title_elem.inner_text().strip() if job_title_elem else ''

            # 薪资
            salary_elem = card.query_selector('.salary')
            salary_text = salary_elem.inner_text().strip() if salary_elem else ''

            # 解析薪资
            from crawler.utils import spider_utils
            salary_min, salary_max, salary_months = spider_utils.parse_salary(salary_text)

            # 公司名称
            company_elem = card.query_selector('.company-name')
            company_name = company_elem.inner_text().strip() if company_elem else ''

            # 职位标签（经验、学历等）
            tags = card.query_selector_all('.job-info .tag-list li')
            tag_texts = [tag.inner_text().strip() for tag in tags]

            # 解析标签
            experience = ''
            education = ''
            city = ''

            for tag in tag_texts:
                if '经验' in tag or '年' in tag or '不限' in tag:
                    experience = spider_utils.standardize_experience(tag)
                elif '学历' in tag or '本科' in tag or '大专' in tag or '硕士' in tag or '博士' in tag:
                    education = spider_utils.standardize_education(tag)
                else:
                    city = spider_utils.standardize_city(tag)

            # 公司信息标签
            company_tags = card.query_selector_all('.company-info .tag-list li')
            company_tag_texts = [tag.inner_text().strip() for tag in company_tags]

            company_size = company_tag_texts[0] if len(company_tag_texts) > 0 else ''
            company_type = company_tag_texts[1] if len(company_tag_texts) > 1 else ''
            industry = company_tag_texts[2] if len(company_tag_texts) > 2 else ''

            # 福利标签
            welfare_tags = card.query_selector_all('.job-card-footer .tag-list span')
            welfare = ','.join([tag.inner_text().strip() for tag in welfare_tags])

            # 职位链接
            link_elem = card.query_selector('a.job-card-left')
            job_url = ''
            if link_elem:
                href = link_elem.get_attribute('href')
                job_url = f"https://www.zhipin.com{href}" if href else ''

            # 构建职位数据
            job = {
                'job_title': job_title,
                'company_name': company_name,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'salary_months': salary_months,
                'city': city,
                'experience': experience,
                'education': education,
                'company_size': company_size,
                'company_type': company_type,
                'industry': industry,
                'job_description': '',  # 需要进入详情页获取
                'job_tags': '',
                'welfare': welfare,
                'source': 'Boss直聘',
                'url': job_url,
                'publish_time': None,
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            return job

        except Exception as e:
            logger.error(f"解析职位卡片详情失败: {e}")
            return None

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
            jobs = self.search_jobs(city, keyword, page)

            if jobs:
                self.jobs_data.extend(jobs)
                logger.info(f"✓ 第{page}页成功获取 {len(jobs)} 条数据")
            else:
                logger.warning(f"第{page}页无数据，停止爬取")
                break

            # 页面之间延时
            self.human_like_delay(3, 5)

    def crawl_all(self, cities: List[str] = None, keywords: List[str] = None, max_pages: int = 2):
        """
        批量爬取多个城市和关键词的职位

        Args:
            cities: 城市列表
            keywords: 关键词列表
            max_pages: 每个关键词最大爬取页数
        """
        cities = cities or TARGET_CITIES[:3]
        keywords = keywords or TARGET_JOBS[:3]

        logger.info(f"="*60)
        logger.info(f"开始批量爬取任务")
        logger.info(f"目标城市: {', '.join(cities)}")
        logger.info(f"职位关键词: {', '.join(keywords)}")
        logger.info(f"="*60)

        # 启动浏览器
        self.start_browser()

        try:
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
                    self.human_like_delay(5, 8)

            logger.info(f"="*60)
            logger.info(f"爬取完成！共获取 {total_jobs} 条职位数据")
            logger.info(f"="*60)

        finally:
            # 关闭浏览器
            self.close_browser()

    def save_to_json(self, filename: str = None):
        """
        保存数据到JSON文件

        Args:
            filename: 文件名
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/raw/boss_playwright_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.jobs_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ 数据已保存到: {filename}")
            logger.info(f"✓ 共保存 {len(self.jobs_data)} 条数据")

        except Exception as e:
            logger.error(f"✗ 保存文件失败: {e}")

    def _get_city_code(self, city_name: str) -> str:
        """获取城市代码"""
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
        }
        return city_codes.get(city_name, '101010100')

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        if not self.jobs_data:
            return {}

        cities = {}
        for job in self.jobs_data:
            city = job.get('city', '未知')
            cities[city] = cities.get(city, 0) + 1

        return {
            'total': len(self.jobs_data),
            'cities': cities,
        }


def main():
    """主函数"""
    if not PLAYWRIGHT_AVAILABLE:
        print("请先安装Playwright:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return

    print("\n" + "="*60)
    print("Boss直聘爬虫 - Playwright版本")
    print("="*60)
    print("说明:")
    print("  - 使用浏览器自动化，模拟真人操作")
    print("  - headless=False 可以看到浏览器操作过程")
    print("  - 如遇到验证码，会暂停等待手动完成")
    print("="*60)

    # 创建爬虫（headless=False 可以看到浏览器）
    spider = BossPlaywrightSpider(headless=False)

    # 小规模测试
    spider.crawl_all(
        cities=['北京'],
        keywords=['Python'],
        max_pages=1
    )

    # 保存数据
    if spider.jobs_data:
        spider.save_to_json()

        # 显示统计
        stats = spider.get_statistics()
        print(f"\n统计信息:")
        print(f"  总职位数: {stats['total']}")
        print(f"  城市分布: {stats['cities']}")

        # 显示样例
        if spider.jobs_data:
            print(f"\n数据样例:")
            job = spider.jobs_data[0]
            print(f"  职位: {job['job_title']}")
            print(f"  公司: {job['company_name']}")
            print(f"  薪资: {job['salary_min']}-{job['salary_max']}")
            print(f"  城市: {job['city']}")


if __name__ == '__main__':
    main()
