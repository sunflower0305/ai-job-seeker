"""
猎聘网Playwright爬虫测试
测试不登录爬取前几页数据
"""

from _bootstrap import PROJECT_ROOT

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
import logging
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LiepinPlaywrightSpider:
    """猎聘网Playwright爬虫"""

    def __init__(self):
        self.jobs_data = []

    async def crawl_jobs(self, keyword="Python", city="010", max_pages=3):
        """
        爬取职位数据

        Args:
            keyword: 搜索关键词
            city: 城市代码 (010=北京, 020=上海, 030=广州, 040=深圳, 050=杭州)
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
                for page_num in range(max_pages):
                    # 猎聘的搜索URL
                    search_url = f"https://www.liepin.com/zhaopin/?key={keyword}&dq={city}&currentPage={page_num}"
                    logger.info(f"访问第 {page_num + 1} 页: {search_url}")

                    await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                    await asyncio.sleep(3)

                    # 等待职位列表加载
                    try:
                        # 猎聘的职位列表选择器
                        await page.wait_for_selector('.job-list-box', timeout=10000)
                        logger.info(f"职位列表加载成功")
                    except:
                        logger.warning("未找到职位列表")
                        # 截图保存当前页面
                        screenshot_path = f"data/debug_liepin_page{page_num + 1}.png"
                        await page.screenshot(path=screenshot_path, full_page=True)
                        logger.info(f"页面截图已保存: {screenshot_path}")
                        break

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
                        # 保存截图用于调试
                        screenshot_path = f"data/debug_liepin_page{page_num + 1}.png"
                        await page.screenshot(path=screenshot_path, full_page=True)
                        logger.info(f"调试截图已保存: {screenshot_path}")

                    # 页面之间延迟
                    await asyncio.sleep(3)

            except Exception as e:
                logger.error(f"爬取过程出错: {e}")
                # 保存错误截图
                await page.screenshot(path='data/error_liepin.png', full_page=True)
                logger.info("错误页面截图已保存: data/error_liepin.png")

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

                    // 尝试多种选择器
                    let jobElements = document.querySelectorAll('.job-card-box');
                    if (jobElements.length === 0) {
                        jobElements = document.querySelectorAll('[class*="job-card"]');
                    }
                    if (jobElements.length === 0) {
                        jobElements = document.querySelectorAll('.job-list-item');
                    }
                    if (jobElements.length === 0) {
                        // 尝试更通用的选择器
                        jobElements = document.querySelectorAll('div[data-job-id]');
                    }

                    console.log('找到职位元素数量:', jobElements.length);

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

                            // 提取所有可能的标签
                            const allText = item.innerText;

                            const job = {
                                job_title: titleEl ? titleEl.innerText.trim() : '',
                                company_name: companyEl ? companyEl.innerText.trim() : '',
                                salary: salaryEl ? salaryEl.innerText.trim() : '',
                                labels: [],
                                company_info: [],
                                tags: [],
                                url: titleEl && titleEl.href ? titleEl.href : '',
                                raw_text: allText.substring(0, 500) // 保存部分文本用于调试
                            };

                            console.log('职位', index + 1, ':', job.job_title, '-', job.company_name, '-', job.salary);

                            if (job.job_title || job.raw_text.length > 0) {
                                jobs.push(job);
                            }
                        } catch (e) {
                            console.log('解析职位失败:', e);
                        }
                    });

                    return jobs;
                }
            """)

            logger.info(f"提取到 {len(jobs_data)} 条原始职位数据")

            # 处理提取的数据
            for job_data in jobs_data:
                job = self._process_job_data(job_data)
                if job:
                    jobs.append(job)

        except Exception as e:
            logger.error(f"提取职位数据失败: {e}")
            import traceback
            logger.error(traceback.format_exc())

        return jobs

    def _process_job_data(self, raw_data):
        """处理职位数据"""
        try:
            # 解析薪资
            salary_text = raw_data.get('salary', '')
            min_salary, max_salary = self._parse_salary(salary_text)

            # 解析标签中的信息 (地点、经验、学历)
            labels = raw_data.get('labels', [])
            city = labels[0] if len(labels) > 0 else ''
            experience = labels[1] if len(labels) > 1 else '不限'
            education = labels[2] if len(labels) > 2 else '不限'

            # 解析公司信息 (行业、规模、类型)
            company_info = raw_data.get('company_info', [])
            industry = company_info[0] if len(company_info) > 0 else ''
            company_size = company_info[1] if len(company_info) > 1 else ''
            company_type = company_info[2] if len(company_info) > 2 else ''

            job = {
                'job_title': raw_data.get('job_title', ''),
                'company_name': raw_data.get('company_name', ''),
                'salary_min': min_salary,
                'salary_max': max_salary,
                'salary_months': 12,
                'city': city,
                'experience': experience,
                'education': education,
                'company_size': company_size,
                'company_type': company_type,
                'industry': industry,
                'job_description': '',
                'job_tags': ','.join(raw_data.get('tags', [])),
                'welfare': ','.join(raw_data.get('tags', [])),
                'source': '猎聘网',
                'url': raw_data.get('url', ''),
                'publish_time': None,
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            return job
        except Exception as e:
            logger.error(f"处理职位数据失败: {e}")
            logger.error(f"原始数据: {raw_data}")
            return None

    def _parse_salary(self, salary_text):
        """解析薪资"""
        if not salary_text or '面议' in salary_text:
            return None, None

        try:
            # 移除空格
            salary_text = salary_text.replace(' ', '').replace(',', '')

            # 匹配类似 "20-35K" 或 "2-3.5万" 的格式
            if 'K' in salary_text or 'k' in salary_text:
                # 格式: 20-35K
                match = re.search(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)[Kk]', salary_text)
                if match:
                    min_salary = int(float(match.group(1)) * 1000)
                    max_salary = int(float(match.group(2)) * 1000)
                    return min_salary, max_salary
            elif '万' in salary_text:
                # 格式: 2-3.5万
                match = re.search(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)万', salary_text)
                if match:
                    min_salary = int(float(match.group(1)) * 10000)
                    max_salary = int(float(match.group(2)) * 10000)
                    return min_salary, max_salary

            logger.warning(f"无法解析薪资格式: {salary_text}")
            return None, None

        except Exception as e:
            logger.warning(f"薪资解析失败: {salary_text}, 错误: {e}")
            return None, None

    def save_to_json(self, filename=None):
        """保存数据到JSON文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/raw/liepin_jobs_{timestamp}.json"

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
                    logger.info(f"  经验: {job['experience']}")
                    logger.info(f"  学历: {job['education']}")

            return filename
        except Exception as e:
            logger.error(f"✗ 保存文件失败: {e}")
            return None


async def main():
    """主函数"""
    spider = LiepinPlaywrightSpider()

    # 测试爬取
    await spider.crawl_jobs(
        keyword="Python",
        city="010",  # 北京
        max_pages=3
    )

    # 保存数据
    if spider.jobs_data:
        spider.save_to_json()
    else:
        logger.warning("未获取到任何数据")


if __name__ == '__main__':
    asyncio.run(main())
