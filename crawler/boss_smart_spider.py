"""
Boss直聘智能爬虫
- 支持登录态复用（Cookie保存/加载）
- 精细控制爬取速度和数量
- 模拟真人操作
- 断点续爬
"""

import json
import time
import random
import os
from datetime import datetime
from typing import List, Dict
import logging
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from config.config import TARGET_CITIES, TARGET_JOBS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BossSmartSpider:
    """Boss直聘智能爬虫"""

    def __init__(self, headless=False, cookie_file='data/cookies.json'):
        """
        初始化爬虫

        Args:
            headless: 是否无头模式
            cookie_file: Cookie保存文件路径
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright未安装")

        self.headless = headless
        self.cookie_file = cookie_file
        self.jobs_data = []
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # 爬取控制参数
        self.config = {
            'delay_range': (3, 6),          # 请求间隔（秒）
            'scroll_delay': (1, 2),         # 滚动延时
            'page_load_wait': (2, 4),       # 页面加载等待
            'max_retry': 3,                 # 最大重试次数
            'jobs_per_page': 30,            # 每页职位数（估计值）
            'max_jobs_per_keyword': 100,    # 每个关键词最大爬取数
            'max_total_jobs': 500,          # 总计最大爬取数
        }

        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_pages': 0,
            'failed_pages': 0,
            'total_jobs': 0,
        }

    def start_browser(self):
        """启动浏览器"""
        logger.info("正在启动浏览器...")
        self.playwright = sync_playwright().start()

        # 启动Chromium
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )

        # 创建浏览器上下文
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN'
        )

        # 加载Cookie（如果存在）
        self._load_cookies()

        # 创建页面
        self.page = self.context.new_page()
        self.page.set_default_timeout(30000)

        # 注入反检测脚本
        self._inject_stealth_scripts()

        logger.info("✓ 浏览器启动成功")

    def _inject_stealth_scripts(self):
        """注入反检测脚本"""
        stealth_js = """
        // 重写navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // 重写Chrome对象
        window.chrome = {
            runtime: {}
        };

        // 重写权限查询
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """
        self.page.add_init_script(stealth_js)

    def _save_cookies(self):
        """保存Cookie"""
        try:
            cookies = self.context.cookies()
            os.makedirs(os.path.dirname(self.cookie_file), exist_ok=True)
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2)
            logger.info(f"✓ Cookie已保存到: {self.cookie_file}")
        except Exception as e:
            logger.error(f"✗ Cookie保存失败: {e}")

    def _load_cookies(self):
        """加载Cookie"""
        try:
            if os.path.exists(self.cookie_file):
                with open(self.cookie_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                self.context.add_cookies(cookies)
                logger.info(f"✓ Cookie已加载: {len(cookies)}个")
                return True
            else:
                logger.info("未找到Cookie文件，需要首次登录")
                return False
        except Exception as e:
            logger.error(f"✗ Cookie加载失败: {e}")
            return False

    def login_if_needed(self, wait_time=60):
        """
        检查登录状态，如需要则等待用户手动登录

        Args:
            wait_time: 等待登录的最大时间（秒）
        """
        logger.info("检查登录状态...")

        # 访问首页
        self.page.goto('https://www.zhipin.com/', wait_until='domcontentloaded')
        time.sleep(3)

        # 检查是否已登录
        try:
            # 查找登录按钮，如果存在说明未登录
            login_btn = self.page.query_selector('.btns .btn-sign-up')

            if login_btn:
                logger.warning("⚠️  未登录状态")
                print("\n" + "="*60)
                print("需要登录Boss直聘")
                print("="*60)
                print("请在打开的浏览器中完成以下操作:")
                print("  1. 点击登录按钮")
                print("  2. 使用手机扫码或账号密码登录")
                print("  3. 登录成功后，按回车继续...")
                print("="*60)

                # 等待用户登录
                input("\n登录完成后按回车继续...")

                # 保存Cookie
                self._save_cookies()
                logger.info("✓ 登录成功，Cookie已保存")
            else:
                logger.info("✓ 已登录状态")

        except Exception as e:
            logger.warning(f"登录检查出现异常: {e}")

    def close_browser(self):
        """关闭浏览器"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("✓ 浏览器已关闭")

    def human_like_delay(self, min_sec=None, max_sec=None):
        """模拟人类操作延时"""
        if min_sec is None:
            min_sec, max_sec = self.config['delay_range']
        delay = random.uniform(min_sec, max_sec)
        logger.debug(f"延时 {delay:.2f} 秒")
        time.sleep(delay)

    def smart_scroll(self):
        """智能滚动页面"""
        # 随机滚动次数和距离
        scroll_times = random.randint(3, 5)

        for i in range(scroll_times):
            # 随机滚动距离
            scroll_distance = random.randint(200, 500)

            # 随机滚动方式
            if random.random() > 0.5:
                # 平滑滚动
                self.page.evaluate(f'''
                    window.scrollBy({{
                        top: {scroll_distance},
                        behavior: 'smooth'
                    }});
                ''')
            else:
                # 直接滚动
                self.page.evaluate(f'window.scrollBy(0, {scroll_distance})')

            # 滚动间隔
            time.sleep(random.uniform(*self.config['scroll_delay']))

        # 偶尔向上滚动一点（模拟真人）
        if random.random() > 0.7:
            self.page.evaluate('window.scrollBy(0, -200)')
            time.sleep(0.5)

    def search_jobs(self, city: str, keyword: str, page_num: int = 1):
        """
        搜索职位

        Args:
            city: 城市
            keyword: 关键词
            page_num: 页码

        Returns:
            职位列表
        """
        try:
            self.stats['total_requests'] += 1

            # 构建URL
            city_code = self._get_city_code(city)
            url = f"https://www.zhipin.com/web/geek/job?query={keyword}&city={city_code}&page={page_num}"

            logger.info(f"第{page_num}页: {city} - {keyword}")

            # 访问页面
            self.page.goto(url, wait_until='domcontentloaded')

            # 等待页面加载
            self.human_like_delay(*self.config['page_load_wait'])

            # 检查验证码
            if self._check_and_handle_captcha():
                logger.warning("检测到验证码，已处理")

            # 等待职位列表
            try:
                self.page.wait_for_selector('.job-list-box', timeout=10000)
            except:
                logger.warning("职位列表加载超时")
                self.stats['failed_pages'] += 1
                return []

            # 智能滚动
            self.smart_scroll()

            # 随机停留
            time.sleep(random.uniform(1, 2))

            # 解析职位
            jobs = self._parse_job_list()

            if jobs:
                self.stats['successful_pages'] += 1
                self.stats['total_jobs'] += len(jobs)
                logger.info(f"✓ 获取 {len(jobs)} 条数据")
            else:
                self.stats['failed_pages'] += 1
                logger.warning(f"✗ 未获取到数据")

            return jobs

        except Exception as e:
            logger.error(f"✗ 搜索失败: {e}")
            self.stats['failed_pages'] += 1
            return []

    def _check_and_handle_captcha(self):
        """检查并处理验证码"""
        try:
            # 检查验证码元素
            captcha_selectors = [
                '.verify-wrap',
                '.captcha-box',
                '[class*="verify"]',
            ]

            for selector in captcha_selectors:
                if self.page.query_selector(selector):
                    logger.warning("⚠️  检测到验证码")
                    print("\n" + "="*60)
                    print("检测到验证码！")
                    print("="*60)
                    print("请在浏览器中完成验证，然后按回车继续...")
                    print("="*60)
                    input("\n验证完成后按回车...")
                    return True

            return False

        except:
            return False

    def _parse_job_list(self):
        """解析职位列表"""
        jobs = []

        try:
            # 获取职位卡片
            job_cards = self.page.query_selector_all('.job-card-wrapper')

            for card in job_cards:
                try:
                    job = self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"解析职位卡片失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"解析职位列表失败: {e}")

        return jobs

    def _parse_job_card(self, card):
        """解析单个职位卡片"""
        try:
            from crawler.utils import spider_utils

            # 职位名称
            job_title = ''
            job_title_elem = card.query_selector('.job-name')
            if job_title_elem:
                job_title = job_title_elem.inner_text().strip()

            # 薪资
            salary_text = ''
            salary_elem = card.query_selector('.salary')
            if salary_elem:
                salary_text = salary_elem.inner_text().strip()

            salary_min, salary_max, salary_months = spider_utils.parse_salary(salary_text)

            # 公司名称
            company_name = ''
            company_elem = card.query_selector('.company-name')
            if company_elem:
                company_name = company_elem.inner_text().strip()

            # 标签
            tags = card.query_selector_all('.job-info .tag-list li')
            tag_texts = [tag.inner_text().strip() for tag in tags]

            experience = ''
            education = ''
            city = ''

            for tag in tag_texts:
                if any(x in tag for x in ['经验', '年', '不限']):
                    experience = spider_utils.standardize_experience(tag)
                elif any(x in tag for x in ['学历', '本科', '大专', '硕士', '博士']):
                    education = spider_utils.standardize_education(tag)
                else:
                    city = spider_utils.standardize_city(tag)

            # 公司信息
            company_tags = card.query_selector_all('.company-info .tag-list li')
            company_tag_texts = [tag.inner_text().strip() for tag in company_tags]

            company_size = company_tag_texts[0] if len(company_tag_texts) > 0 else ''
            company_type = company_tag_texts[1] if len(company_tag_texts) > 1 else ''
            industry = company_tag_texts[2] if len(company_tag_texts) > 2 else ''

            # 福利
            welfare_tags = card.query_selector_all('.job-card-footer .tag-list span')
            welfare = ','.join([tag.inner_text().strip() for tag in welfare_tags])

            # 链接
            job_url = ''
            link_elem = card.query_selector('a.job-card-left')
            if link_elem:
                href = link_elem.get_attribute('href')
                job_url = f"https://www.zhipin.com{href}" if href else ''

            return {
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
                'job_description': '',
                'job_tags': '',
                'welfare': welfare,
                'source': 'Boss直聘',
                'url': job_url,
                'publish_time': None,
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.debug(f"解析职位详情失败: {e}")
            return None

    def crawl_controlled(self, cities: List[str], keywords: List[str],
                        max_jobs_per_keyword: int = 50, max_total: int = 500):
        """
        受控爬取

        Args:
            cities: 城市列表
            keywords: 关键词列表
            max_jobs_per_keyword: 每个关键词最大爬取数
            max_total: 总计最大爬取数
        """
        logger.info("="*60)
        logger.info("开始受控爬取")
        logger.info(f"城市: {', '.join(cities)}")
        logger.info(f"关键词: {', '.join(keywords)}")
        logger.info(f"每个关键词最多: {max_jobs_per_keyword} 条")
        logger.info(f"总计最多: {max_total} 条")
        logger.info("="*60)

        # 启动浏览器
        self.start_browser()

        # 检查登录
        self.login_if_needed()

        try:
            for city in cities:
                for keyword in keywords:
                    # 检查总数限制
                    if len(self.jobs_data) >= max_total:
                        logger.info(f"已达到总数限制 ({max_total})，停止爬取")
                        return

                    logger.info(f"\n开始爬取: {city} - {keyword}")

                    keyword_jobs = 0
                    page = 1
                    max_pages = (max_jobs_per_keyword // 30) + 1

                    while keyword_jobs < max_jobs_per_keyword and page <= max_pages:
                        # 检查总数
                        if len(self.jobs_data) >= max_total:
                            break

                        # 爬取一页
                        jobs = self.search_jobs(city, keyword, page)

                        if not jobs:
                            logger.warning(f"第{page}页无数据，跳过")
                            break

                        # 添加数据
                        for job in jobs:
                            if len(self.jobs_data) < max_total and keyword_jobs < max_jobs_per_keyword:
                                self.jobs_data.append(job)
                                keyword_jobs += 1

                        logger.info(f"{city}-{keyword}: 已获取 {keyword_jobs}/{max_jobs_per_keyword} 条")

                        # 下一页
                        page += 1

                        # 页面间延时
                        self.human_like_delay()

                    # 关键词间延时
                    logger.info(f"✓ {city}-{keyword} 完成，休息一下...")
                    self.human_like_delay(5, 10)

            # 完成
            logger.info("="*60)
            logger.info(f"爬取完成！总计: {len(self.jobs_data)} 条")
            logger.info("="*60)

        finally:
            # 保存Cookie
            self._save_cookies()
            # 关闭浏览器
            self.close_browser()

    def save_to_json(self, filename: str = None):
        """保存数据"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/raw/boss_smart_{timestamp}.json"

        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.jobs_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ 数据已保存: {filename}")
            logger.info(f"✓ 共 {len(self.jobs_data)} 条")

            return filename

        except Exception as e:
            logger.error(f"✗ 保存失败: {e}")
            return None

    def print_stats(self):
        """打印统计信息"""
        print("\n" + "="*60)
        print("爬取统计")
        print("="*60)
        print(f"总请求数: {self.stats['total_requests']}")
        print(f"成功页数: {self.stats['successful_pages']}")
        print(f"失败页数: {self.stats['failed_pages']}")
        print(f"总职位数: {len(self.jobs_data)}")

        if self.stats['successful_pages'] > 0:
            print(f"成功率: {self.stats['successful_pages']/self.stats['total_requests']*100:.1f}%")
            print(f"平均每页: {len(self.jobs_data)/self.stats['successful_pages']:.1f} 条")

        print("="*60)

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


def main():
    """主函数"""
    if not PLAYWRIGHT_AVAILABLE:
        print("请先安装Playwright:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return

    print("\n" + "="*60)
    print("Boss直聘智能爬虫")
    print("="*60)
    print("特性:")
    print("  ✓ 登录态复用（Cookie自动保存/加载）")
    print("  ✓ 智能爬取控制（限制数量和速度）")
    print("  ✓ 模拟真人操作（随机延时、滚动）")
    print("  ✓ 自动处理验证码（暂停等待）")
    print("="*60)

    # 创建爬虫
    spider = BossSmartSpider(headless=False)

    # 受控爬取
    spider.crawl_controlled(
        cities=['北京', '上海'],
        keywords=['Python', 'Java'],
        max_jobs_per_keyword=30,  # 每个关键词最多30条
        max_total=100              # 总计最多100条
    )

    # 保存数据
    if spider.jobs_data:
        filename = spider.save_to_json()

        # 统计信息
        spider.print_stats()

        # 样例展示
        print("\n数据样例（前3条）:")
        for i, job in enumerate(spider.jobs_data[:3], 1):
            print(f"\n{i}. {job['job_title']} - {job['company_name']}")
            print(f"   薪资: {job['salary_min']}-{job['salary_max']}")
            print(f"   城市: {job['city']} | 经验: {job['experience']} | 学历: {job['education']}")


if __name__ == '__main__':
    main()
