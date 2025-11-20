"""
数据分析模块
负责对清洗后的招聘数据进行多维度统计分析
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
from datetime import datetime
from collections import Counter
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobDataAnalyzer:
    """招聘数据分析器"""

    def __init__(self, data_source=None):
        """
        初始化分析器

        Args:
            data_source: 数据源，可以是文件路径或DataFrame
        """
        self.df = None
        self.data_source = data_source
        self.analysis_results = {}

    def load_data(self, data_source=None):
        """
        加载数据

        Args:
            data_source: 数据源（CSV/JSON文件路径或DataFrame）
        """
        if data_source:
            self.data_source = data_source

        if self.data_source is None:
            raise ValueError("请指定数据源")

        logger.info(f"正在加载数据...")

        # 如果已经是DataFrame，直接使用
        if isinstance(self.data_source, pd.DataFrame):
            self.df = self.data_source
            logger.info(f"✓ 已加载DataFrame，共 {len(self.df)} 条数据")
            return self.df

        # 从文件加载
        file_path = Path(self.data_source)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if file_path.suffix == '.csv':
            self.df = pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            self.df = pd.read_json(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")

        logger.info(f"✓ 成功加载 {len(self.df)} 条数据")
        logger.info(f"✓ 数据字段: {list(self.df.columns)[:10]}...")

        return self.df

    def get_basic_statistics(self):
        """获取基础统计信息"""
        logger.info("\n" + "="*60)
        logger.info("基础统计分析")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        stats = {
            'total_jobs': len(self.df),
            'total_companies': self.df['company_name'].nunique() if 'company_name' in self.df.columns else 0,
            'total_cities': self.df['city'].nunique() if 'city' in self.df.columns else 0,
            'data_fields': len(self.df.columns),
            'date_range': {}
        }

        # 时间范围
        if 'publish_time' in self.df.columns:
            try:
                self.df['publish_time'] = pd.to_datetime(self.df['publish_time'])
                stats['date_range'] = {
                    'start': str(self.df['publish_time'].min()),
                    'end': str(self.df['publish_time'].max())
                }
            except:
                pass

        # 数据来源统计
        if 'source' in self.df.columns:
            stats['sources'] = self.df['source'].value_counts().to_dict()

        self.analysis_results['basic_statistics'] = stats

        logger.info(f"职位总数: {stats['total_jobs']}")
        logger.info(f"公司总数: {stats['total_companies']}")
        logger.info(f"城市总数: {stats['total_cities']}")
        if stats['date_range']:
            logger.info(f"数据时间范围: {stats['date_range']['start']} ~ {stats['date_range']['end']}")

        return stats

    def analyze_salary(self):
        """薪资分析"""
        logger.info("\n" + "="*60)
        logger.info("薪资分析")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        salary_analysis = {}

        # 整体薪资统计
        if 'salary_avg' in self.df.columns:
            salary_analysis['overall'] = {
                'mean': float(self.df['salary_avg'].mean()),
                'median': float(self.df['salary_avg'].median()),
                'std': float(self.df['salary_avg'].std()),
                'min': float(self.df['salary_avg'].min()),
                'max': float(self.df['salary_avg'].max()),
                'q1': float(self.df['salary_avg'].quantile(0.25)),
                'q3': float(self.df['salary_avg'].quantile(0.75))
            }

            logger.info(f"平均薪资: {salary_analysis['overall']['mean']:.0f} 元/月")
            logger.info(f"中位数薪资: {salary_analysis['overall']['median']:.0f} 元/月")
            logger.info(f"薪资范围: {salary_analysis['overall']['min']:.0f} - {salary_analysis['overall']['max']:.0f} 元/月")

        # 按城市分析
        if 'city' in self.df.columns and 'salary_avg' in self.df.columns:
            city_salary = self.df.groupby('city')['salary_avg'].agg([
                ('count', 'count'),
                ('mean', 'mean'),
                ('median', 'median'),
                ('min', 'min'),
                ('max', 'max')
            ]).round(0)

            # 转换为字典，按平均薪资排序
            city_salary_sorted = city_salary.sort_values('mean', ascending=False)
            salary_analysis['by_city'] = city_salary_sorted.to_dict('index')

            logger.info(f"\n薪资最高的5个城市:")
            for city, data in list(salary_analysis['by_city'].items())[:5]:
                logger.info(f"  {city}: 平均 {data['mean']:.0f} 元/月 ({data['count']:.0f} 个职位)")

        # 按学历分析
        if 'education' in self.df.columns and 'salary_avg' in self.df.columns:
            edu_salary = self.df.groupby('education')['salary_avg'].agg([
                ('count', 'count'),
                ('mean', 'mean'),
                ('median', 'median')
            ]).round(0)

            edu_salary_sorted = edu_salary.sort_values('mean', ascending=False)
            salary_analysis['by_education'] = edu_salary_sorted.to_dict('index')

            logger.info(f"\n按学历薪资分析:")
            for edu, data in salary_analysis['by_education'].items():
                logger.info(f"  {edu}: 平均 {data['mean']:.0f} 元/月 ({data['count']:.0f} 个职位)")

        # 按经验分析
        if 'experience' in self.df.columns and 'salary_avg' in self.df.columns:
            exp_salary = self.df.groupby('experience')['salary_avg'].agg([
                ('count', 'count'),
                ('mean', 'mean'),
                ('median', 'median')
            ]).round(0)

            # 定义经验排序顺序
            exp_order = ['不限', '1年以下', '1-3年', '3-5年', '5-10年', '10年以上']
            exp_salary = exp_salary.reindex([e for e in exp_order if e in exp_salary.index])

            salary_analysis['by_experience'] = exp_salary.to_dict('index')

            logger.info(f"\n按工作经验薪资分析:")
            for exp, data in salary_analysis['by_experience'].items():
                logger.info(f"  {exp}: 平均 {data['mean']:.0f} 元/月 ({data['count']:.0f} 个职位)")

        # 按行业分析
        if 'industry' in self.df.columns and 'salary_avg' in self.df.columns:
            industry_salary = self.df.groupby('industry')['salary_avg'].agg([
                ('count', 'count'),
                ('mean', 'mean'),
                ('median', 'median')
            ]).round(0)

            industry_salary_sorted = industry_salary.sort_values('mean', ascending=False)
            salary_analysis['by_industry'] = industry_salary_sorted.head(10).to_dict('index')

            logger.info(f"\n薪资最高的10个行业:")
            for industry, data in list(salary_analysis['by_industry'].items())[:10]:
                logger.info(f"  {industry}: 平均 {data['mean']:.0f} 元/月 ({data['count']:.0f} 个职位)")

        self.analysis_results['salary_analysis'] = salary_analysis
        return salary_analysis

    def analyze_skills(self):
        """技能需求分析"""
        logger.info("\n" + "="*60)
        logger.info("技能需求分析")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        skills_analysis = {}

        if 'job_tags' not in self.df.columns:
            logger.warning("未找到job_tags字段，跳过技能分析")
            return skills_analysis

        # 统计所有技能
        all_skills = []
        for tags in self.df['job_tags'].dropna():
            if tags and str(tags).strip():
                skills = [s.strip() for s in str(tags).split(',') if s.strip()]
                all_skills.extend(skills)

        if not all_skills:
            logger.warning("没有找到技能标签数据")
            return skills_analysis

        # 技能频次统计
        skill_counter = Counter(all_skills)
        top_skills = skill_counter.most_common(50)

        skills_analysis['top_skills'] = [
            {'skill': skill, 'count': count}
            for skill, count in top_skills
        ]

        logger.info(f"\n最热门的20个技能:")
        for i, (skill, count) in enumerate(top_skills[:20], 1):
            percentage = (count / len(self.df)) * 100
            logger.info(f"  {i:2d}. {skill:20s}: {count:4d} ({percentage:5.1f}%)")

        # 按技能分类统计
        skill_categories = {
            'languages': 'skills_languages',
            'web_frameworks': 'skills_web_frameworks',
            'databases': 'skills_databases',
            'big_data': 'skills_big_data',
            'ml_ai': 'skills_ml_ai',
            'devops': 'skills_devops',
            'mobile': 'skills_mobile'
        }

        category_stats = {}
        for category, column in skill_categories.items():
            if column in self.df.columns:
                skills_in_category = []
                for tags in self.df[column].dropna():
                    if tags and str(tags).strip():
                        skills = [s.strip() for s in str(tags).split(',') if s.strip()]
                        skills_in_category.extend(skills)

                if skills_in_category:
                    counter = Counter(skills_in_category)
                    category_stats[category] = {
                        'total': len(skills_in_category),
                        'unique': len(counter),
                        'top_5': counter.most_common(5)
                    }

        skills_analysis['by_category'] = category_stats

        # 技能与薪资关系
        if 'salary_avg' in self.df.columns:
            skill_salary = {}

            for skill, _ in top_skills[:30]:  # 分析前30个热门技能
                # 找出包含该技能的职位
                mask = self.df['job_tags'].fillna('').str.contains(skill, case=False, regex=False)
                jobs_with_skill = self.df[mask]

                if len(jobs_with_skill) > 0:
                    skill_salary[skill] = {
                        'count': len(jobs_with_skill),
                        'avg_salary': float(jobs_with_skill['salary_avg'].mean()),
                        'median_salary': float(jobs_with_skill['salary_avg'].median())
                    }

            # 按平均薪资排序
            skill_salary_sorted = sorted(
                skill_salary.items(),
                key=lambda x: x[1]['avg_salary'],
                reverse=True
            )

            skills_analysis['skill_salary'] = dict(skill_salary_sorted[:20])

            logger.info(f"\n薪资最高的10个技能:")
            for skill, data in skill_salary_sorted[:10]:
                logger.info(f"  {skill:20s}: 平均 {data['avg_salary']:.0f} 元/月 ({data['count']} 个职位)")

        self.analysis_results['skills_analysis'] = skills_analysis
        return skills_analysis

    def analyze_job_distribution(self):
        """职位分布分析"""
        logger.info("\n" + "="*60)
        logger.info("职位分布分析")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        distribution = {}

        # 城市分布
        if 'city' in self.df.columns:
            city_dist = self.df['city'].value_counts().head(20)
            distribution['by_city'] = city_dist.to_dict()

            logger.info(f"\n职位数量最多的10个城市:")
            for city, count in list(distribution['by_city'].items())[:10]:
                percentage = (count / len(self.df)) * 100
                logger.info(f"  {city}: {count} ({percentage:.1f}%)")

        # 学历要求分布
        if 'education' in self.df.columns:
            edu_dist = self.df['education'].value_counts()
            distribution['by_education'] = edu_dist.to_dict()

            logger.info(f"\n学历要求分布:")
            for edu, count in distribution['by_education'].items():
                percentage = (count / len(self.df)) * 100
                logger.info(f"  {edu}: {count} ({percentage:.1f}%)")

        # 经验要求分布
        if 'experience' in self.df.columns:
            exp_dist = self.df['experience'].value_counts()
            distribution['by_experience'] = exp_dist.to_dict()

            logger.info(f"\n工作经验要求分布:")
            for exp, count in distribution['by_experience'].items():
                percentage = (count / len(self.df)) * 100
                logger.info(f"  {exp}: {count} ({percentage:.1f}%)")

        # 公司规模分布
        if 'company_size' in self.df.columns:
            size_dist = self.df['company_size'].value_counts()
            distribution['by_company_size'] = size_dist.to_dict()

            logger.info(f"\n公司规模分布:")
            for size, count in list(distribution['by_company_size'].items())[:10]:
                percentage = (count / len(self.df)) * 100
                logger.info(f"  {size}: {count} ({percentage:.1f}%)")

        # 行业分布
        if 'industry' in self.df.columns:
            industry_dist = self.df['industry'].value_counts().head(15)
            distribution['by_industry'] = industry_dist.to_dict()

            logger.info(f"\n行业分布 (Top 15):")
            for industry, count in distribution['by_industry'].items():
                percentage = (count / len(self.df)) * 100
                logger.info(f"  {industry}: {count} ({percentage:.1f}%)")

        self.analysis_results['distribution'] = distribution
        return distribution

    def analyze_correlations(self):
        """相关性分析"""
        logger.info("\n" + "="*60)
        logger.info("相关性分析")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        correlations = {}

        # 选择数值型字段
        numeric_cols = ['salary_min', 'salary_max', 'salary_avg', 'salary_months']
        numeric_cols = [col for col in numeric_cols if col in self.df.columns]

        if len(numeric_cols) < 2:
            logger.warning("数值字段不足，跳过相关性分析")
            return correlations

        # 计算相关系数矩阵
        corr_matrix = self.df[numeric_cols].corr()
        correlations['numeric_correlation'] = corr_matrix.to_dict()

        logger.info(f"\n数值字段相关性矩阵:")
        logger.info(f"\n{corr_matrix.round(3)}")

        self.analysis_results['correlations'] = correlations
        return correlations

    def generate_summary_report(self):
        """生成综合分析报告"""
        logger.info("\n" + "="*60)
        logger.info("生成综合分析报告")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        # 执行所有分析
        if not self.analysis_results:
            self.get_basic_statistics()
            self.analyze_salary()
            self.analyze_skills()
            self.analyze_job_distribution()
            self.analyze_correlations()

        # 添加元数据
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_records': len(self.df),
                'data_fields': list(self.df.columns)
            },
            'analysis': self.analysis_results
        }

        logger.info(f"✓ 分析报告生成完成")

        return report

    def save_report(self, output_file=None):
        """
        保存分析报告

        Args:
            output_file: 输出文件路径
        """
        if not self.analysis_results:
            self.generate_summary_report()

        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"data/processed/analysis_report_{timestamp}.json"

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_records': len(self.df) if self.df is not None else 0,
            },
            'analysis': self.analysis_results
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"✓ 分析报告已保存: {output_path}")
        return str(output_path)

    def analyze_all(self):
        """执行所有分析"""
        logger.info("\n" + "="*80)
        logger.info("开始全面数据分析")
        logger.info("="*80)

        self.get_basic_statistics()
        self.analyze_salary()
        self.analyze_skills()
        self.analyze_job_distribution()
        self.analyze_correlations()

        logger.info("\n" + "="*80)
        logger.info("数据分析完成！")
        logger.info("="*80)

        return self.analysis_results


def main():
    """主函数 - 示例用法"""
    import glob
    import os

    # 获取项目根目录
    project_root = Path(__file__).parent.parent

    # 查找最新的清洗数据文件
    data_files = glob.glob(str(project_root / 'data/processed/cleaned_jobs_*.csv'))
    if not data_files:
        data_files = glob.glob(str(project_root / 'data/processed/test_cleaned_jobs.csv'))

    if not data_files:
        logger.error("未找到清洗后的数据文件")
        logger.info("请先运行数据清洗模块生成数据")
        return

    # 使用最新的文件
    latest_file = max(data_files)
    logger.info(f"使用数据文件: {latest_file}")

    # 创建分析器
    analyzer = JobDataAnalyzer(latest_file)

    # 加载数据
    analyzer.load_data()

    # 执行分析
    analyzer.analyze_all()

    # 保存报告
    report_file = project_root / 'data/processed' / f'analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    analyzer.save_report(str(report_file))


if __name__ == '__main__':
    main()
