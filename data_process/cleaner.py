"""
数据清洗模块
负责清洗从爬虫获取的原始招聘数据
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import re
from pathlib import Path
from html import unescape
import html.parser

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清洗类"""

    # 技能标签标准化映射表
    SKILL_MAPPING = {
        # 编程语言
        'python': 'Python',
        'java': 'Java',
        'javascript': 'JavaScript',
        'js': 'JavaScript',
        'typescript': 'TypeScript',
        'ts': 'TypeScript',
        'c++': 'C++',
        'cpp': 'C++',
        'c#': 'C#',
        'csharp': 'C#',
        'go': 'Go',
        'golang': 'Go',
        'rust': 'Rust',
        'php': 'PHP',
        'ruby': 'Ruby',
        'swift': 'Swift',
        'kotlin': 'Kotlin',
        'scala': 'Scala',
        'r': 'R',
        'matlab': 'MATLAB',
        'shell': 'Shell',
        'bash': 'Bash',

        # Web框架
        'django': 'Django',
        'flask': 'Flask',
        'fastapi': 'FastAPI',
        'spring': 'Spring',
        'springboot': 'Spring Boot',
        'spring boot': 'Spring Boot',
        'react': 'React',
        'reactjs': 'React',
        'vue': 'Vue',
        'vuejs': 'Vue.js',
        'vue.js': 'Vue.js',
        'angular': 'Angular',
        'nodejs': 'Node.js',
        'node.js': 'Node.js',
        'node': 'Node.js',
        'express': 'Express',
        'nextjs': 'Next.js',
        'next.js': 'Next.js',
        'nuxt': 'Nuxt.js',

        # 数据库
        'mysql': 'MySQL',
        'postgresql': 'PostgreSQL',
        'postgres': 'PostgreSQL',
        'mongodb': 'MongoDB',
        'mongo': 'MongoDB',
        'redis': 'Redis',
        'elasticsearch': 'Elasticsearch',
        'es': 'Elasticsearch',
        'oracle': 'Oracle',
        'sqlserver': 'SQL Server',
        'sql server': 'SQL Server',
        'sqlite': 'SQLite',
        'cassandra': 'Cassandra',

        # 大数据
        'hadoop': 'Hadoop',
        'spark': 'Spark',
        'kafka': 'Kafka',
        'flink': 'Flink',
        'hive': 'Hive',
        'hbase': 'HBase',

        # 机器学习/AI
        'tensorflow': 'TensorFlow',
        'pytorch': 'PyTorch',
        'keras': 'Keras',
        'scikit-learn': 'Scikit-learn',
        'sklearn': 'Scikit-learn',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'opencv': 'OpenCV',
        'nlp': 'NLP',

        # 云计算/DevOps
        'docker': 'Docker',
        'kubernetes': 'Kubernetes',
        'k8s': 'Kubernetes',
        'aws': 'AWS',
        'azure': 'Azure',
        'gcp': 'Google Cloud',
        'google cloud': 'Google Cloud',
        'jenkins': 'Jenkins',
        'gitlab': 'GitLab',
        'github': 'GitHub',
        'git': 'Git',
        'ci/cd': 'CI/CD',
        'terraform': 'Terraform',

        # 移动开发
        'android': 'Android',
        'ios': 'iOS',
        'flutter': 'Flutter',
        'react native': 'React Native',
        'react-native': 'React Native',

        # 其他工具和技术
        'linux': 'Linux',
        'unix': 'Unix',
        'nginx': 'Nginx',
        'apache': 'Apache',
        'tomcat': 'Tomcat',
        'microservices': '微服务',
        '微服务': '微服务',
        'restful': 'RESTful',
        'rest': 'REST',
        'graphql': 'GraphQL',
        'grpc': 'gRPC',
        'rabbitmq': 'RabbitMQ',
        'activemq': 'ActiveMQ',
    }

    # 技能分类
    SKILL_CATEGORIES = {
        'languages': ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala'],
        'web_frameworks': ['Django', 'Flask', 'FastAPI', 'Spring', 'Spring Boot', 'React', 'Vue', 'Vue.js', 'Angular', 'Node.js', 'Express'],
        'databases': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Oracle', 'SQL Server'],
        'big_data': ['Hadoop', 'Spark', 'Kafka', 'Flink', 'Hive', 'HBase'],
        'ml_ai': ['TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy', 'OpenCV', 'NLP'],
        'devops': ['Docker', 'Kubernetes', 'AWS', 'Azure', 'Google Cloud', 'Jenkins', 'Git', 'CI/CD'],
        'mobile': ['Android', 'iOS', 'Flutter', 'React Native'],
    }

    def __init__(self, input_file=None):
        """
        初始化数据清洗器

        Args:
            input_file: 输入文件路径
        """
        self.input_file = input_file
        self.df = None
        self.original_count = 0
        self.quality_report = {}

    def load_data(self, file_path=None):
        """
        加载数据

        Args:
            file_path: 数据文件路径（JSON格式）
        """
        if file_path:
            self.input_file = file_path

        if not self.input_file:
            raise ValueError("请指定输入文件路径")

        logger.info(f"正在加载数据: {self.input_file}")

        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.df = pd.DataFrame(data)
            self.original_count = len(self.df)

            logger.info(f"✓ 成功加载 {self.original_count} 条数据")
            logger.info(f"✓ 数据字段: {list(self.df.columns)}")

            return self.df

        except Exception as e:
            logger.error(f"✗ 加载数据失败: {e}")
            raise

    def handle_missing_values(self):
        """处理缺失值"""
        logger.info("\n" + "="*60)
        logger.info("处理缺失值")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        before_count = len(self.df)

        # 1. 删除职位标题或公司名称为空的记录
        self.df = self.df.dropna(subset=['job_title', 'company_name'])
        self.df = self.df[self.df['job_title'].str.strip() != '']
        self.df = self.df[self.df['company_name'].str.strip() != '']

        logger.info(f"✓ 删除标题或公司为空的记录: {before_count - len(self.df)} 条")

        # 2. 删除薪资信息缺失的记录
        before_salary = len(self.df)
        self.df = self.df.dropna(subset=['salary_min', 'salary_max'])
        logger.info(f"✓ 删除薪资缺失的记录: {before_salary - len(self.df)} 条")

        # 3. 填充其他字段的缺失值
        fill_values = {
            'city': '未知',
            'experience': '不限',
            'education': '不限',
            'company_size': '未知',
            'company_type': '未知',
            'industry': '未知',
            'job_description': '',
            'job_tags': '',
            'welfare': '',
            'url': '',
        }

        # 使用 fillna 填充，不使用 inplace
        for col, value in fill_values.items():
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna(value)

        logger.info(f"✓ 填充其他字段缺失值")
        logger.info(f"✓ 处理后剩余: {len(self.df)} 条数据")

    def remove_duplicates(self):
        """去除重复数据"""
        logger.info("\n" + "="*60)
        logger.info("去除重复数据")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        before_count = len(self.df)

        # 基于职位标题和公司名称去重
        self.df = self.df.drop_duplicates(subset=['job_title', 'company_name'], keep='first')

        removed = before_count - len(self.df)
        logger.info(f"✓ 删除重复记录: {removed} 条")
        logger.info(f"✓ 剩余数据: {len(self.df)} 条")

    def handle_outliers(self):
        """处理异常值"""
        logger.info("\n" + "="*60)
        logger.info("处理异常值")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        before_count = len(self.df)

        # 1. 删除薪资异常的记录
        # 最低薪资应该 > 0 且 < 100000 (月薪10万以内)
        # 最高薪资应该 > 最低薪资
        self.df = self.df[
            (self.df['salary_min'] > 0) &
            (self.df['salary_min'] < 100000) &
            (self.df['salary_max'] > self.df['salary_min']) &
            (self.df['salary_max'] < 200000)
        ]

        logger.info(f"✓ 删除薪资异常记录: {before_count - len(self.df)} 条")

        # 2. 使用IQR方法检测薪资异常值
        q1 = self.df['salary_min'].quantile(0.25)
        q3 = self.df['salary_min'].quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - 3 * iqr  # 使用3倍IQR，保留更多数据
        upper_bound = q3 + 3 * iqr

        before_iqr = len(self.df)
        self.df = self.df[
            (self.df['salary_min'] >= lower_bound) &
            (self.df['salary_min'] <= upper_bound)
        ]

        logger.info(f"✓ IQR方法删除异常值: {before_iqr - len(self.df)} 条")
        logger.info(f"✓ 薪资范围: {lower_bound:.0f} - {upper_bound:.0f}")
        logger.info(f"✓ 剩余数据: {len(self.df)} 条")

    def clean_text_fields(self):
        """清理文本字段（去除HTML、特殊字符等）"""
        logger.info("\n" + "="*60)
        logger.info("清理文本字段")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        # 1. 清理职位描述
        if 'job_description' in self.df.columns:
            self.df['job_description'] = self.df['job_description'].apply(self._clean_text)
            logger.info("✓ 职位描述清理完成")

        # 2. 清理福利待遇
        if 'welfare' in self.df.columns:
            self.df['welfare'] = self.df['welfare'].apply(self._clean_text)
            logger.info("✓ 福利待遇清理完成")

        # 3. 清理职位标签
        if 'job_tags' in self.df.columns:
            self.df['job_tags'] = self.df['job_tags'].apply(self._clean_tags)
            logger.info("✓ 职位标签清理完成")

        # 4. 清理公司名称（去除多余字符）
        if 'company_name' in self.df.columns:
            self.df['company_name'] = self.df['company_name'].apply(self._clean_company_name)
            logger.info("✓ 公司名称清理完成")

    def _clean_text(self, text):
        """
        清理文本内容
        - 去除HTML标签
        - 去除特殊字符
        - 规范化空白字符
        """
        if pd.isna(text) or not text:
            return ''

        text = str(text)

        # 1. 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)

        # 2. 解码HTML实体
        text = unescape(text)

        # 3. 去除URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        # 4. 去除邮箱
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)

        # 5. 去除电话号码
        text = re.sub(r'\b\d{3,4}[-\s]?\d{7,8}\b', '', text)
        text = re.sub(r'\b1[3-9]\d{9}\b', '', text)

        # 6. 去除特殊字符但保留中文标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。、；：！？（）《》""''【】—…\-,./]', '', text)

        # 7. 规范化空白字符
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def _clean_tags(self, tags):
        """
        清理标签字段
        - 标准化分隔符
        - 去除重复
        - 去除空标签
        """
        if pd.isna(tags) or not tags:
            return ''

        tags = str(tags)

        # 1. 去除HTML标签
        tags = re.sub(r'<[^>]+>', '', tags)

        # 2. 标准化分隔符（统一使用逗号）
        tags = re.sub(r'[、|/；;]', ',', tags)

        # 3. 分割、清理、去重
        tag_list = [tag.strip() for tag in tags.split(',')]
        tag_list = [tag for tag in tag_list if tag and len(tag) > 0]

        # 4. 去除重复（保持顺序）
        seen = set()
        unique_tags = []
        for tag in tag_list:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                unique_tags.append(tag)

        # 5. 标准化技能标签
        standardized_tags = [self._standardize_skill(tag) for tag in unique_tags]

        return ','.join(standardized_tags)

    def _standardize_skill(self, skill):
        """
        标准化单个技能标签

        Args:
            skill: 原始技能名称

        Returns:
            标准化后的技能名称
        """
        if not skill:
            return skill

        # 转换为小写进行匹配
        skill_lower = skill.lower().strip()

        # 在映射表中查找标准化名称
        if skill_lower in self.SKILL_MAPPING:
            return self.SKILL_MAPPING[skill_lower]

        # 如果不在映射表中，返回首字母大写的版本
        return skill.strip().title()

    def extract_skills_from_description(self):
        """
        从职位描述中提取技能关键词
        """
        logger.info("\n" + "="*60)
        logger.info("从职位描述中提取技能")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        if 'job_description' not in self.df.columns:
            logger.warning("职位描述字段不存在，跳过技能提取")
            return

        # 创建一个新列存储从描述中提取的技能
        def extract_skills(description, existing_tags):
            if pd.isna(description):
                return existing_tags

            description_lower = str(description).lower()
            extracted_skills = set()

            # 在描述中搜索已知的技能关键词
            for skill_key, skill_value in self.SKILL_MAPPING.items():
                # 使用词边界匹配，避免部分匹配
                pattern = r'\b' + re.escape(skill_key) + r'\b'
                if re.search(pattern, description_lower):
                    extracted_skills.add(skill_value)

            # 合并已有标签和提取的技能
            existing_set = set()
            if existing_tags:
                existing_set = {tag.strip() for tag in str(existing_tags).split(',')}

            # 合并并去重
            all_skills = existing_set.union(extracted_skills)

            return ','.join(sorted(all_skills)) if all_skills else existing_tags

        # 提取并更新技能标签
        if 'job_tags' in self.df.columns:
            self.df['job_tags'] = self.df.apply(
                lambda row: extract_skills(row['job_description'], row['job_tags']),
                axis=1
            )
            logger.info("✓ 技能提取完成")
        else:
            logger.warning("job_tags 字段不存在，无法更新")

    def categorize_skills(self):
        """
        对技能标签进行分类
        """
        logger.info("\n" + "="*60)
        logger.info("技能标签分类")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        if 'job_tags' not in self.df.columns:
            logger.warning("job_tags 字段不存在，跳过技能分类")
            return

        # 为每个类别创建新列
        for category in self.SKILL_CATEGORIES.keys():
            column_name = f'skills_{category}'
            self.df[column_name] = self.df['job_tags'].apply(
                lambda tags: self._categorize_tags(tags, category)
            )

        logger.info(f"✓ 技能分类完成，创建了 {len(self.SKILL_CATEGORIES)} 个分类字段")

    def _categorize_tags(self, tags, category):
        """
        将标签分类到指定类别

        Args:
            tags: 标签字符串
            category: 类别名称

        Returns:
            该类别的技能列表（逗号分隔）
        """
        if pd.isna(tags) or not tags:
            return ''

        tag_list = [tag.strip() for tag in str(tags).split(',')]
        category_skills = self.SKILL_CATEGORIES.get(category, [])

        # 筛选出属于该类别的技能
        matched_skills = [tag for tag in tag_list if tag in category_skills]

        return ','.join(matched_skills) if matched_skills else ''

    def _clean_company_name(self, name):
        """
        清理公司名称
        - 去除多余空格
        - 去除特殊字符
        """
        if pd.isna(name) or not name:
            return '未知'

        name = str(name).strip()

        # 1. 去除HTML标签
        name = re.sub(r'<[^>]+>', '', name)

        # 2. 去除多余空格
        name = re.sub(r'\s+', ' ', name)

        # 3. 去除特殊字符（保留括号和基本符号）
        name = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s()（）\-&]', '', name)

        name = name.strip()

        return name if name else '未知'

    def standardize_data(self):
        """标准化数据"""
        logger.info("\n" + "="*60)
        logger.info("标准化数据")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        # 1. 标准化城市名称
        self.df['city'] = self.df['city'].apply(self._standardize_city)
        logger.info("✓ 城市名称标准化完成")

        # 2. 标准化学历要求
        self.df['education'] = self.df['education'].apply(self._standardize_education)
        logger.info("✓ 学历要求标准化完成")

        # 3. 标准化工作经验
        self.df['experience'] = self.df['experience'].apply(self._standardize_experience)
        logger.info("✓ 工作经验标准化完成")

        # 4. 清理职位标题（移除多余空格和换行）
        self.df['job_title'] = self.df['job_title'].str.replace('\n', ' ').str.strip()
        self.df['job_title'] = self.df['job_title'].str.replace(r'\s+', ' ', regex=True)
        logger.info("✓ 职位标题清理完成")

        # 5. 计算平均薪资
        self.df['salary_avg'] = (self.df['salary_min'] + self.df['salary_max']) / 2
        logger.info("✓ 计算平均薪资完成")

        # 6. 计算年薪
        self.df['salary_yearly_min'] = self.df['salary_min'] * self.df['salary_months']
        self.df['salary_yearly_max'] = self.df['salary_max'] * self.df['salary_months']
        self.df['salary_yearly_avg'] = self.df['salary_avg'] * self.df['salary_months']
        logger.info("✓ 计算年薪完成")

    def _standardize_city(self, city):
        """标准化城市名称"""
        if pd.isna(city) or not city:
            return '未知'

        # 移除"市"字
        city = str(city).replace('市', '').replace('省', '').strip()

        # 城市别名映射
        city_map = {
            '北京市': '北京',
            '上海市': '上海',
            '广州市': '广州',
            '深圳市': '深圳',
            '重庆市': '重庆',
            '天津市': '天津',
        }

        return city_map.get(city, city)

    def _standardize_education(self, edu):
        """标准化学历要求"""
        if pd.isna(edu) or not edu:
            return '不限'

        edu = str(edu).strip()

        # 学历映射
        if '博士' in edu:
            return '博士'
        elif '硕士' in edu or '研究生' in edu:
            return '硕士'
        elif '本科' in edu or '学士' in edu:
            return '本科'
        elif '大专' in edu or '专科' in edu:
            return '大专'
        elif '高中' in edu or '中专' in edu:
            return '高中'
        elif '不限' in edu or '无' in edu:
            return '不限'
        else:
            return '不限'

    def _standardize_experience(self, exp):
        """标准化工作经验"""
        if pd.isna(exp) or not exp:
            return '不限'

        exp = str(exp).strip()

        # 经验映射 - 按照从具体到一般的顺序匹配
        if '不限' in exp or '无' in exp or '应届' in exp:
            return '不限'
        elif '5' in exp and '10' in exp:  # 先匹配 5-10年
            return '5-10年'
        elif '10' in exp or ('10年' in exp):  # 再匹配 10年以上
            return '10年以上'
        elif '3' in exp and '5' in exp:  # 匹配 3-5年
            return '3-5年'
        elif '5' in exp:  # 单独的5年
            return '3-5年'
        elif '1' in exp and '3' in exp:  # 匹配 1-3年
            return '1-3年'
        elif '3' in exp:  # 单独的3年
            return '1-3年'
        elif '1' in exp:
            return '1年以下'
        else:
            return '不限'

    def generate_quality_report(self):
        """生成数据质量报告"""
        logger.info("\n" + "="*60)
        logger.info("生成数据质量报告")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        report = {
            'original_count': self.original_count,
            'final_count': len(self.df),
            'removed_count': self.original_count - len(self.df),
            'removal_rate': f"{((self.original_count - len(self.df)) / self.original_count * 100):.2f}%",
            'fields_count': len(self.df.columns),
            'fields': list(self.df.columns),
        }

        # 字段完整性统计
        field_stats = {}
        for col in self.df.columns:
            non_null = self.df[col].notna().sum()
            field_stats[col] = {
                'non_null': int(non_null),
                'null': int(len(self.df) - non_null),
                'completeness': f"{(non_null / len(self.df) * 100):.2f}%"
            }

        report['field_stats'] = field_stats

        # 数据分布统计
        report['city_distribution'] = self.df['city'].value_counts().to_dict()
        report['education_distribution'] = self.df['education'].value_counts().to_dict()
        report['experience_distribution'] = self.df['experience'].value_counts().to_dict()
        report['source_distribution'] = self.df['source'].value_counts().to_dict()

        # 薪资统计
        report['salary_stats'] = {
            'min': int(self.df['salary_min'].min()),
            'max': int(self.df['salary_max'].max()),
            'avg_min': int(self.df['salary_min'].mean()),
            'avg_max': int(self.df['salary_max'].mean()),
            'median_avg': int(self.df['salary_avg'].median()),
        }

        self.quality_report = report

        # 打印报告
        logger.info(f"\n数据量统计:")
        logger.info(f"  原始数据: {report['original_count']} 条")
        logger.info(f"  清洗后: {report['final_count']} 条")
        logger.info(f"  删除: {report['removed_count']} 条 ({report['removal_rate']})")

        logger.info(f"\n薪资统计 (元/月):")
        logger.info(f"  最低薪资: {report['salary_stats']['min']} - {report['salary_stats']['max']}")
        logger.info(f"  平均最低薪资: {report['salary_stats']['avg_min']}")
        logger.info(f"  平均最高薪资: {report['salary_stats']['avg_max']}")
        logger.info(f"  中位数薪资: {report['salary_stats']['median_avg']}")

        logger.info(f"\n城市分布:")
        for city, count in list(report['city_distribution'].items())[:10]:
            logger.info(f"  {city}: {count} 条")

        logger.info(f"\n学历分布:")
        for edu, count in report['education_distribution'].items():
            logger.info(f"  {edu}: {count} 条")

        logger.info(f"\n经验分布:")
        for exp, count in report['experience_distribution'].items():
            logger.info(f"  {exp}: {count} 条")

        return report

    def save_cleaned_data(self, output_file=None, save_json=True):
        """
        保存清洗后的数据

        Args:
            output_file: 输出文件路径（不含扩展名）
            save_json: 是否同时保存JSON格式
        """
        if self.df is None:
            raise ValueError("请先加载并清洗数据")

        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"data/processed/cleaned_jobs_{timestamp}"

        # 确保目录存在
        output_dir = Path(output_file).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存为CSV
        csv_file = f"{output_file}.csv"
        self.df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        logger.info(f"✓ CSV数据已保存: {csv_file}")

        # 保存为JSON
        if save_json:
            json_file = f"{output_file}.json"
            self.df.to_json(json_file, orient='records', force_ascii=False, indent=2)
            logger.info(f"✓ JSON数据已保存: {json_file}")

        # 保存质量报告
        if self.quality_report:
            report_file = f"{output_file}_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.quality_report, f, ensure_ascii=False, indent=2)
            logger.info(f"✓ 质量报告已保存: {report_file}")

        return csv_file

    def clean(self):
        """
        执行完整的数据清洗流程
        """
        logger.info("\n" + "="*60)
        logger.info("开始数据清洗")
        logger.info("="*60)

        # 1. 处理缺失值
        self.handle_missing_values()

        # 2. 去除重复数据
        self.remove_duplicates()

        # 3. 处理异常值
        self.handle_outliers()

        # 4. 标准化数据
        self.standardize_data()

        # 5. 清理文本字段
        self.clean_text_fields()

        # 6. 从职位描述中提取技能
        self.extract_skills_from_description()

        # 7. 技能分类
        self.categorize_skills()

        # 8. 生成质量报告
        self.generate_quality_report()

        logger.info("\n" + "="*60)
        logger.info("数据清洗完成！")
        logger.info("="*60)

        return self.df


def main():
    """主函数 - 示例用法"""
    import glob

    # 查找最新的爬虫数据文件
    data_files = glob.glob('data/raw/liepin_jobs_*.json')
    if not data_files:
        logger.error("未找到爬虫数据文件")
        return

    # 使用最新的文件
    latest_file = max(data_files)
    logger.info(f"使用数据文件: {latest_file}")

    # 创建清洗器
    cleaner = DataCleaner(latest_file)

    # 加载数据
    cleaner.load_data()

    # 执行清洗
    cleaner.clean()

    # 保存清洗后的数据
    cleaner.save_cleaned_data()


class DataValidator:
    """数据验证器类"""

    def __init__(self, df):
        """
        初始化验证器

        Args:
            df: 要验证的DataFrame
        """
        self.df = df
        self.validation_errors = []
        self.validation_warnings = []

    def validate_all(self):
        """执行所有验证检查"""
        logger.info("\n" + "="*60)
        logger.info("数据验证")
        logger.info("="*60)

        self.validate_required_fields()
        self.validate_data_types()
        self.validate_value_ranges()
        self.validate_data_consistency()

        return self.get_validation_report()

    def validate_required_fields(self):
        """验证必填字段"""
        logger.info("\n检查必填字段...")

        required_fields = ['job_title', 'company_name', 'salary_min', 'salary_max']

        for field in required_fields:
            if field not in self.df.columns:
                self.validation_errors.append(f"缺少必填字段: {field}")
                logger.error(f"✗ 缺少必填字段: {field}")
            else:
                null_count = self.df[field].isna().sum()
                if null_count > 0:
                    self.validation_warnings.append(
                        f"字段 {field} 有 {null_count} 条空值"
                    )
                    logger.warning(f"⚠ 字段 {field} 有 {null_count} 条空值")
                else:
                    logger.info(f"✓ 字段 {field} 完整")

    def validate_data_types(self):
        """验证数据类型"""
        logger.info("\n检查数据类型...")

        # 检查薪资字段是否为数值型
        numeric_fields = ['salary_min', 'salary_max', 'salary_months']

        for field in numeric_fields:
            if field in self.df.columns:
                try:
                    pd.to_numeric(self.df[field], errors='raise')
                    logger.info(f"✓ 字段 {field} 类型正确")
                except (ValueError, TypeError):
                    self.validation_errors.append(f"字段 {field} 包含非数值数据")
                    logger.error(f"✗ 字段 {field} 包含非数值数据")

        # 检查文本字段
        text_fields = ['job_title', 'company_name', 'city']

        for field in text_fields:
            if field in self.df.columns:
                non_string_count = sum(
                    not isinstance(val, str) and pd.notna(val)
                    for val in self.df[field]
                )
                if non_string_count > 0:
                    self.validation_warnings.append(
                        f"字段 {field} 有 {non_string_count} 条非文本数据"
                    )
                    logger.warning(f"⚠ 字段 {field} 有 {non_string_count} 条非文本数据")
                else:
                    logger.info(f"✓ 字段 {field} 类型正确")

    def validate_value_ranges(self):
        """验证数值范围"""
        logger.info("\n检查数值范围...")

        # 检查薪资范围
        if 'salary_min' in self.df.columns:
            invalid_min = self.df[
                (self.df['salary_min'] < 1000) | (self.df['salary_min'] > 100000)
            ]
            if len(invalid_min) > 0:
                self.validation_warnings.append(
                    f"有 {len(invalid_min)} 条记录的最低薪资超出合理范围 (1000-100000)"
                )
                logger.warning(f"⚠ 有 {len(invalid_min)} 条记录的最低薪资超出合理范围")
            else:
                logger.info("✓ 最低薪资范围正常")

        if 'salary_max' in self.df.columns:
            invalid_max = self.df[
                (self.df['salary_max'] < 1000) | (self.df['salary_max'] > 200000)
            ]
            if len(invalid_max) > 0:
                self.validation_warnings.append(
                    f"有 {len(invalid_max)} 条记录的最高薪资超出合理范围 (1000-200000)"
                )
                logger.warning(f"⚠ 有 {len(invalid_max)} 条记录的最高薪资超出合理范围")
            else:
                logger.info("✓ 最高薪资范围正常")

        # 检查薪资月数
        if 'salary_months' in self.df.columns:
            invalid_months = self.df[
                (self.df['salary_months'] < 12) | (self.df['salary_months'] > 24)
            ]
            if len(invalid_months) > 0:
                self.validation_warnings.append(
                    f"有 {len(invalid_months)} 条记录的薪资月数超出合理范围 (12-24)"
                )
                logger.warning(f"⚠ 有 {len(invalid_months)} 条记录的薪资月数超出合理范围")
            else:
                logger.info("✓ 薪资月数范围正常")

    def validate_data_consistency(self):
        """验证数据一致性"""
        logger.info("\n检查数据一致性...")

        # 检查最高薪资是否大于最低薪资
        if 'salary_min' in self.df.columns and 'salary_max' in self.df.columns:
            inconsistent = self.df[self.df['salary_max'] <= self.df['salary_min']]
            if len(inconsistent) > 0:
                self.validation_errors.append(
                    f"有 {len(inconsistent)} 条记录的最高薪资不大于最低薪资"
                )
                logger.error(f"✗ 有 {len(inconsistent)} 条记录的最高薪资不大于最低薪资")
            else:
                logger.info("✓ 薪资一致性检查通过")

        # 检查重复数据
        if 'job_title' in self.df.columns and 'company_name' in self.df.columns:
            duplicates = self.df.duplicated(subset=['job_title', 'company_name'])
            duplicate_count = duplicates.sum()
            if duplicate_count > 0:
                self.validation_warnings.append(
                    f"发现 {duplicate_count} 条重复记录"
                )
                logger.warning(f"⚠ 发现 {duplicate_count} 条重复记录")
            else:
                logger.info("✓ 无重复数据")

    def get_validation_report(self):
        """获取验证报告"""
        report = {
            'total_records': len(self.df),
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
            'error_count': len(self.validation_errors),
            'warning_count': len(self.validation_warnings),
            'is_valid': len(self.validation_errors) == 0
        }

        logger.info("\n" + "="*60)
        logger.info("验证报告")
        logger.info("="*60)
        logger.info(f"总记录数: {report['total_records']}")
        logger.info(f"错误数: {report['error_count']}")
        logger.info(f"警告数: {report['warning_count']}")

        if report['errors']:
            logger.info("\n错误详情:")
            for error in report['errors']:
                logger.error(f"  ✗ {error}")

        if report['warnings']:
            logger.info("\n警告详情:")
            for warning in report['warnings']:
                logger.warning(f"  ⚠ {warning}")

        if report['is_valid']:
            logger.info("\n✓ 数据验证通过！")
        else:
            logger.error("\n✗ 数据验证失败，请修复错误后重试")

        return report


if __name__ == '__main__':
    main()
