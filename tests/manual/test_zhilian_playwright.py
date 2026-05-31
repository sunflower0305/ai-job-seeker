"""
智联招聘Playwright爬虫测试
测试不登录爬取前几页数据
"""

from _bootstrap import PROJECT_ROOT

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ZhilianPlaywrightSpider:
    """智联招聘Playwright爬虫"""

    def __init__(self):
        self.jobs_data = []

    async def crawl_jobs(self, keyword="Python", city="北京", max_pages=3):
        """
        爬取职位数据

        Args:
            keyword: 搜索关键词
            city: 城市
            max_pages: 最大页数
        """
        async with async_playwright() as p:
            logger.info("启动浏览器...")
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            try:
                # 访问智联招聘搜索页面
                search_url = f"https://www.zhaopin.com/sou/jl{self._get_city_code(city)}/kw{keyword}"
                logger.info(f"访问搜索页面: {search_url}")

                await page.goto(search_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(3)

                for page_num in range(1, max_pages + 1):
                    logger.info(f"正在爬取第 {page_num} 页...")

                    # 等待职位列表加载
                    try:
                        await page.wait_for_selector('.positionlist__content', timeout=10000)
                    except:
                        logger.warning("未找到职位列表，可能需要登录或被反爬")
                        # 截图保存当前页面
                        screenshot_path = f"data/debug_zhilian_page{page_num}.png"
                        await page.screenshot(path=screenshot_path)
                        logger.info(f"页面截图已保存: {screenshot_path}")
                        break

                    # 获取页面内容
                    await asyncio.sleep(2)

                    # 提取职位信息
                    jobs = await self._extract_jobs_from_page(page)
                    logger.info(f"第 {page_num} 页获取到 {len(jobs)} 条职位")
                    self.jobs_data.extend(jobs)

                    # 翻页
                    if page_num < max_pages:
                        try:
                            # 查找下一页按钮
                            next_button = await page.query_selector('.positionlist__pagination .next')
                            if next_button:
                                await next_button.click()
                                await asyncio.sleep(3)
                            else:
                                logger.info("没有下一页了")
                                break
                        except Exception as e:
                            logger.warning(f"翻页失败: {e}")
                            break

            except Exception as e:
                logger.error(f"爬取过程出错: {e}")
                # 保存错误截图
                await page.screenshot(path='data/error_screenshot.png')
                logger.info("错误页面截图已保存: data/error_screenshot.png")

            finally:
                await browser.close()

        logger.info(f"爬取完成，共获取 {len(self.jobs_data)} 条职位数据")

    async def _extract_jobs_from_page(self, page):
        """从页面提取职位信息"""
        jobs = []

        try:
            # 使用JavaScript提取数据
            jobs_data = await page.evaluate("""
                () => {
                    const jobs = [];
                    const jobElements = document.querySelectorAll('.joblist-box__item');

                    jobElements.forEach(item => {
                        try {
                            const titleEl = item.querySelector('.joblist-box__job-name');
                            const companyEl = item.querySelector('.companyinfo__top-name');
                            const salaryEl = item.querySelector('.joblist-box__item-salary');
                            const tagsEl = item.querySelectorAll('.joblist-box__item-tag');
                            const welfareEl = item.querySelectorAll('.joblist-box__item-welfare span');

                            const job = {
                                job_title: titleEl ? titleEl.innerText.trim() : '',
                                company_name: companyEl ? companyEl.innerText.trim() : '',
                                salary: salaryEl ? salaryEl.innerText.trim() : '',
                                tags: Array.from(tagsEl).map(tag => tag.innerText.trim()),
                                welfare: Array.from(welfareEl).map(w => w.innerText.trim()),
                                url: titleEl ? titleEl.href : ''
                            };

                            if (job.job_title) {
                                jobs.push(job);
                            }
                        } catch (e) {
                            console.log('解析职位失败:', e);
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

            # 解析标签中的城市、经验、学历
            tags = raw_data.get('tags', [])
            city = tags[0] if len(tags) > 0 else ''
            experience = tags[1] if len(tags) > 1 else '不限'
            education = tags[2] if len(tags) > 2 else '不限'

            job = {
                'job_title': raw_data.get('job_title', ''),
                'company_name': raw_data.get('company_name', ''),
                'salary_min': min_salary,
                'salary_max': max_salary,
                'salary_months': 12,
                'city': city,
                'experience': experience,
                'education': education,
                'company_size': '',
                'company_type': '',
                'industry': '',
                'job_description': '',
                'job_tags': ','.join(tags),
                'welfare': ','.join(raw_data.get('welfare', [])),
                'source': '智联招聘',
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
            # 移除空格和特殊字符
            salary_text = salary_text.replace(' ', '').replace('元/月', '')
            salary_text = salary_text.upper().replace('K', '')

            if '-' in salary_text:
                parts = salary_text.split('-')
                min_salary = int(float(parts[0]) * 1000)
                max_salary = int(float(parts[1]) * 1000)
                return min_salary, max_salary
            else:
                salary = int(float(salary_text) * 1000)
                return salary, salary
        except Exception as e:
            logger.warning(f"薪资解析失败: {salary_text}, 错误: {e}")
            return None, None

    def _get_city_code(self, city_name):
        """获取城市代码"""
        city_codes = {
            '北京': '530',
            '上海': '538',
            '广州': '763',
            '深圳': '765',
            '杭州': '653',
            '成都': '801',
        }
        return city_codes.get(city_name, '530')

    def save_to_json(self, filename=None):
        """保存数据到JSON文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/raw/zhilian_playwright_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.jobs_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ 数据已保存到: {filename}")
            logger.info(f"✓ 共保存 {len(self.jobs_data)} 条数据")

            # 打印前3条数据作为示例
            if self.jobs_data:
                logger.info("\n前3条数据示例:")
                for i, job in enumerate(self.jobs_data[:3], 1):
                    logger.info(f"\n职位 {i}:")
                    logger.info(f"  标题: {job['job_title']}")
                    logger.info(f"  公司: {job['company_name']}")
                    logger.info(f"  薪资: {job['salary_min']}-{job['salary_max']}")
                    logger.info(f"  城市: {job['city']}")

        except Exception as e:
            logger.error(f"✗ 保存文件失败: {e}")


async def main():
    """主函数"""
    spider = ZhilianPlaywrightSpider()

    # 测试爬取
    await spider.crawl_jobs(
        keyword="Python",
        city="北京",
        max_pages=3
    )

    # 保存数据
    if spider.jobs_data:
        spider.save_to_json()
    else:
        logger.warning("未获取到任何数据")


if __name__ == '__main__':
    asyncio.run(main())
