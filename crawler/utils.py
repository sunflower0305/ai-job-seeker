"""
爬虫工具函数
提供通用的爬虫功能支持
"""

import time
import random
import logging
from config.config import SPIDER_CONFIG

# 尝试导入fake_useragent，如果失败则使用内置列表
try:
    from fake_useragent import UserAgent
    USE_FAKE_UA = True
except ImportError:
    USE_FAKE_UA = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpiderUtils:
    """爬虫工具类"""

    def __init__(self):
        if USE_FAKE_UA:
            try:
                self.ua = UserAgent()
            except:
                self.ua = None
        else:
            self.ua = None

        # 备用User-Agent列表
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]

    def get_random_headers(self):
        """
        获取随机请求头

        Returns:
            dict: 包含User-Agent的请求头字典
        """
        # 优先使用fake_useragent
        if self.ua:
            try:
                user_agent = self.ua.random
            except:
                user_agent = random.choice(self.user_agents)
        else:
            user_agent = random.choice(self.user_agents)

        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    @staticmethod
    def random_delay():
        """
        随机延时，避免请求过快
        """
        delay = random.uniform(*SPIDER_CONFIG['delay_range'])
        time.sleep(delay)
        logger.debug(f"延时 {delay:.2f} 秒")

    @staticmethod
    def parse_salary(salary_text):
        """
        解析薪资字符串

        Args:
            salary_text: 薪资文本，如 "10k-15k"、"8-10K·13薪"

        Returns:
            tuple: (最低薪资, 最高薪资, 月数)
        """
        if not salary_text or salary_text in ['面议', '薪资面议']:
            return None, None, 12

        try:
            # 移除空格和·后的内容
            salary_text = salary_text.replace(' ', '').split('·')[0]

            # 处理月数信息
            months = 12
            if '薪' in salary_text:
                months_text = salary_text.split('薪')[0]
                if months_text.isdigit():
                    months = int(months_text)
                salary_text = salary_text.split('薪')[-1]

            # 提取薪资范围
            salary_text = salary_text.upper().replace('K', '').replace('千', '')

            if '-' in salary_text:
                parts = salary_text.split('-')
                min_salary = float(parts[0]) * 1000
                max_salary = float(parts[1]) * 1000
            elif '以上' in salary_text:
                min_salary = float(salary_text.replace('以上', '')) * 1000
                max_salary = min_salary * 1.5
            else:
                min_salary = max_salary = float(salary_text) * 1000

            return int(min_salary), int(max_salary), months

        except Exception as e:
            logger.warning(f"薪资解析失败: {salary_text}, 错误: {e}")
            return None, None, 12

    @staticmethod
    def standardize_city(city_text):
        """
        标准化城市名称

        Args:
            city_text: 城市文本

        Returns:
            str: 标准化后的城市名
        """
        # 去除"市"、"省"等后缀
        city_text = city_text.replace('市', '').replace('省', '')

        # 处理特殊情况
        city_map = {
            '北京市': '北京',
            '上海市': '上海',
            '重庆市': '重庆',
            '天津市': '天津',
        }

        return city_map.get(city_text, city_text)

    @staticmethod
    def standardize_experience(exp_text):
        """
        标准化工作经验

        Args:
            exp_text: 经验文本，如"1-3年"、"3年以上"

        Returns:
            str: 标准化后的经验要求
        """
        if not exp_text:
            return '不限'

        exp_text = exp_text.replace('经验', '').replace('工作', '').strip()

        if '不限' in exp_text or '无' in exp_text or '应届' in exp_text:
            return '不限'
        elif '1年' in exp_text or '1-' in exp_text:
            return '1-3年'
        elif '3年' in exp_text or '3-' in exp_text:
            return '3-5年'
        elif '5年' in exp_text or '5-' in exp_text:
            return '5-10年'
        elif '10年' in exp_text or '10' in exp_text:
            return '10年以上'
        else:
            return exp_text

    @staticmethod
    def standardize_education(edu_text):
        """
        标准化学历要求

        Args:
            edu_text: 学历文本

        Returns:
            str: 标准化后的学历
        """
        if not edu_text:
            return '不限'

        edu_text = edu_text.replace('及以上', '').strip()

        edu_map = {
            '不限': '不限',
            '初中': '初中',
            '高中': '高中',
            '中专': '中专',
            '大专': '大专',
            '本科': '本科',
            '硕士': '硕士',
            '博士': '博士',
        }

        for key in edu_map:
            if key in edu_text:
                return edu_map[key]

        return '不限'


# 创建工具实例
spider_utils = SpiderUtils()
