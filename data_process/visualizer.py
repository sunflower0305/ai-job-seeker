"""
数据可视化模块
负责生成各类数据可视化图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
from collections import Counter

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 设置seaborn样式
sns.set_style("whitegrid")
sns.set_palette("husl")


class JobDataVisualizer:
    """招聘数据可视化器"""

    def __init__(self, data_source=None, output_dir='data/visualizations'):
        """
        初始化可视化器

        Args:
            data_source: 数据源（文件路径或DataFrame）
            output_dir: 图表输出目录
        """
        self.df = None
        self.data_source = data_source
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 图表配置
        self.figure_size = (12, 6)
        self.dpi = 100

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
        return self.df

    def plot_salary_distribution(self, save_file=None):
        """绘制薪资分布直方图"""
        logger.info("生成薪资分布图...")

        if 'salary_avg' not in self.df.columns:
            logger.warning("未找到salary_avg字段，跳过")
            return None

        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

        # 绘制直方图
        ax.hist(self.df['salary_avg'], bins=30, edgecolor='black', alpha=0.7)

        # 添加平均值和中位数线
        mean_salary = self.df['salary_avg'].mean()
        median_salary = self.df['salary_avg'].median()

        ax.axvline(mean_salary, color='red', linestyle='--', linewidth=2,
                   label=f'平均值: {mean_salary:.0f}')
        ax.axvline(median_salary, color='green', linestyle='--', linewidth=2,
                   label=f'中位数: {median_salary:.0f}')

        ax.set_xlabel('平均薪资 (元/月)', fontsize=12)
        ax.set_ylabel('职位数量', fontsize=12)
        ax.set_title('薪资分布直方图', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_file is None:
            save_file = self.output_dir / 'salary_distribution.png'

        plt.savefig(save_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ 薪资分布图已保存: {save_file}")
        return str(save_file)

    def plot_salary_by_city(self, top_n=10, save_file=None):
        """绘制各城市薪资对比图"""
        logger.info(f"生成城市薪资对比图 (Top {top_n})...")

        if 'city' not in self.df.columns or 'salary_avg' not in self.df.columns:
            logger.warning("未找到必要字段，跳过")
            return None

        # 计算各城市平均薪资
        city_salary = self.df.groupby('city')['salary_avg'].agg([
            ('平均薪资', 'mean'),
            ('职位数量', 'count')
        ]).round(0)

        # 筛选职位数量>5的城市，按平均薪资排序
        city_salary = city_salary[city_salary['职位数量'] >= 5]
        city_salary = city_salary.sort_values('平均薪资', ascending=False).head(top_n)

        # 创建图表
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

        # 绘制条形图
        bars = ax.barh(city_salary.index, city_salary['平均薪资'])

        # 为每个条形添加数值标签
        for i, (idx, row) in enumerate(city_salary.iterrows()):
            ax.text(row['平均薪资'], i, f" {row['平均薪资']:.0f}元 ({row['职位数量']:.0f}个)",
                   va='center', fontsize=10)

        ax.set_xlabel('平均薪资 (元/月)', fontsize=12)
        ax.set_ylabel('城市', fontsize=12)
        ax.set_title(f'各城市平均薪资对比 (Top {top_n})', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        if save_file is None:
            save_file = self.output_dir / 'salary_by_city.png'

        plt.savefig(save_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ 城市薪资对比图已保存: {save_file}")
        return str(save_file)

    def plot_salary_by_education(self, save_file=None):
        """绘制学历与薪资关系图"""
        logger.info("生成学历薪资关系图...")

        if 'education' not in self.df.columns or 'salary_avg' not in self.df.columns:
            logger.warning("未找到必要字段，跳过")
            return None

        # 定义学历顺序
        edu_order = ['不限', '高中', '大专', '本科', '硕士', '博士']
        available_edu = [e for e in edu_order if e in self.df['education'].values]

        if not available_edu:
            logger.warning("没有有效的学历数据")
            return None

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=self.dpi)

        # 左图：箱线图
        edu_data = [self.df[self.df['education'] == edu]['salary_avg'].values
                    for edu in available_edu]

        bp = ax1.boxplot(edu_data, labels=available_edu, patch_artist=True)

        # 美化箱线图
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
            patch.set_alpha(0.7)

        ax1.set_xlabel('学历要求', fontsize=12)
        ax1.set_ylabel('薪资 (元/月)', fontsize=12)
        ax1.set_title('不同学历薪资分布（箱线图）', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')

        # 右图：平均薪资条形图
        edu_salary = self.df.groupby('education')['salary_avg'].agg([
            ('平均薪资', 'mean'),
            ('职位数量', 'count')
        ]).round(0)
        edu_salary = edu_salary.reindex(available_edu)

        bars = ax2.bar(range(len(available_edu)), edu_salary['平均薪资'])

        # 添加数值标签
        for i, (idx, row) in enumerate(edu_salary.iterrows()):
            ax2.text(i, row['平均薪资'], f"{row['平均薪资']:.0f}\n({row['职位数量']:.0f}个)",
                    ha='center', va='bottom', fontsize=10)

        ax2.set_xticks(range(len(available_edu)))
        ax2.set_xticklabels(available_edu)
        ax2.set_xlabel('学历要求', fontsize=12)
        ax2.set_ylabel('平均薪资 (元/月)', fontsize=12)
        ax2.set_title('不同学历平均薪资对比', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save_file is None:
            save_file = self.output_dir / 'salary_by_education.png'

        plt.savefig(save_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ 学历薪资关系图已保存: {save_file}")
        return str(save_file)

    def plot_salary_by_experience(self, save_file=None):
        """绘制工作经验与薪资关系图"""
        logger.info("生成经验薪资关系图...")

        if 'experience' not in self.df.columns or 'salary_avg' not in self.df.columns:
            logger.warning("未找到必要字段，跳过")
            return None

        # 定义经验顺序
        exp_order = ['不限', '1年以下', '1-3年', '3-5年', '5-10年', '10年以上']
        available_exp = [e for e in exp_order if e in self.df['experience'].values]

        if not available_exp:
            logger.warning("没有有效的经验数据")
            return None

        # 计算统计数据
        exp_salary = self.df.groupby('experience')['salary_avg'].agg([
            ('平均薪资', 'mean'),
            ('最低薪资', 'min'),
            ('最高薪资', 'max'),
            ('职位数量', 'count')
        ]).round(0)
        exp_salary = exp_salary.reindex(available_exp)

        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

        x = range(len(available_exp))

        # 绘制线图
        ax.plot(x, exp_salary['平均薪资'], marker='o', linewidth=2, markersize=8,
               label='平均薪资', color='blue')

        # 填充最高最低范围
        ax.fill_between(x, exp_salary['最低薪资'], exp_salary['最高薪资'],
                        alpha=0.2, label='薪资范围')

        # 添加数值标签
        for i, (idx, row) in enumerate(exp_salary.iterrows()):
            ax.text(i, row['平均薪资'], f"{row['平均薪资']:.0f}",
                   ha='center', va='bottom', fontsize=10)

        ax.set_xticks(x)
        ax.set_xticklabels(available_exp)
        ax.set_xlabel('工作经验', fontsize=12)
        ax.set_ylabel('薪资 (元/月)', fontsize=12)
        ax.set_title('工作经验与薪资关系', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_file is None:
            save_file = self.output_dir / 'salary_by_experience.png'

        plt.savefig(save_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ 经验薪资关系图已保存: {save_file}")
        return str(save_file)

    def plot_skills_wordcloud(self, max_words=100, save_file=None):
        """生成技能词云图"""
        logger.info("生成技能词云图...")

        if 'job_tags' not in self.df.columns:
            logger.warning("未找到job_tags字段，跳过")
            return None

        # 收集所有技能
        all_skills = []
        for tags in self.df['job_tags'].dropna():
            if tags and str(tags).strip():
                skills = [s.strip() for s in str(tags).split(',') if s.strip()]
                all_skills.extend(skills)

        if not all_skills:
            logger.warning("没有找到技能数据")
            return None

        # 统计词频
        skill_freq = Counter(all_skills)

        # 生成词云
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            max_words=max_words,
            relative_scaling=0.5,
            min_font_size=10,
            font_path=None,  # 使用系统默认字体
            colormap='viridis'
        ).generate_from_frequencies(skill_freq)

        # 绘制
        fig, ax = plt.subplots(figsize=(14, 7), dpi=self.dpi)
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('技能需求词云图', fontsize=16, fontweight='bold', pad=20)

        plt.tight_layout()

        if save_file is None:
            save_file = self.output_dir / 'skills_wordcloud.png'

        plt.savefig(save_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ 技能词云图已保存: {save_file}")
        return str(save_file)

    def plot_top_skills(self, top_n=20, save_file=None):
        """绘制热门技能Top N"""
        logger.info(f"生成热门技能Top {top_n}图...")

        if 'job_tags' not in self.df.columns:
            logger.warning("未找到job_tags字段，跳过")
            return None

        # 收集所有技能
        all_skills = []
        for tags in self.df['job_tags'].dropna():
            if tags and str(tags).strip():
                skills = [s.strip() for s in str(tags).split(',') if s.strip()]
                all_skills.extend(skills)

        if not all_skills:
            logger.warning("没有找到技能数据")
            return None

        # 统计Top N
        skill_counter = Counter(all_skills)
        top_skills = skill_counter.most_common(top_n)

        skills = [s[0] for s in top_skills]
        counts = [s[1] for s in top_skills]
        percentages = [(c / len(self.df)) * 100 for c in counts]

        # 绘制
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

        bars = ax.barh(range(len(skills)), counts)

        # 添加标签
        for i, (skill, count, pct) in enumerate(zip(skills, counts, percentages)):
            ax.text(count, i, f" {count} ({pct:.1f}%)",
                   va='center', fontsize=9)

        ax.set_yticks(range(len(skills)))
        ax.set_yticklabels(skills)
        ax.set_xlabel('职位数量', fontsize=12)
        ax.set_ylabel('技能', fontsize=12)
        ax.set_title(f'最热门技能 Top {top_n}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        if save_file is None:
            save_file = self.output_dir / f'top_{top_n}_skills.png'

        plt.savefig(save_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ 热门技能图已保存: {save_file}")
        return str(save_file)

    def plot_industry_distribution(self, top_n=10, save_file=None):
        """绘制行业分布饼图"""
        logger.info(f"生成行业分布图 (Top {top_n})...")

        if 'industry' not in self.df.columns:
            logger.warning("未找到industry字段，跳过")
            return None

        # 统计行业分布
        industry_counts = self.df['industry'].value_counts().head(top_n)

        # 如果分类太多，将其他合并
        if len(self.df['industry'].unique()) > top_n:
            other_count = len(self.df) - industry_counts.sum()
            industry_counts['其他'] = other_count

        # 绘制饼图
        fig, ax = plt.subplots(figsize=(10, 10), dpi=self.dpi)

        colors = sns.color_palette('husl', len(industry_counts))

        wedges, texts, autotexts = ax.pie(
            industry_counts.values,
            labels=industry_counts.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 10}
        )

        # 美化百分比文字
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title(f'行业分布 (Top {top_n})', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        if save_file is None:
            save_file = self.output_dir / 'industry_distribution.png'

        plt.savefig(save_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ 行业分布图已保存: {save_file}")
        return str(save_file)

    def generate_all_charts(self):
        """生成所有图表"""
        logger.info("\n" + "="*60)
        logger.info("开始生成所有图表")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        chart_files = {}

        # 生成各类图表
        chart_files['salary_distribution'] = self.plot_salary_distribution()
        chart_files['salary_by_city'] = self.plot_salary_by_city()
        chart_files['salary_by_education'] = self.plot_salary_by_education()
        chart_files['salary_by_experience'] = self.plot_salary_by_experience()
        chart_files['skills_wordcloud'] = self.plot_skills_wordcloud()
        chart_files['top_skills'] = self.plot_top_skills()
        chart_files['industry_distribution'] = self.plot_industry_distribution()

        # 过滤掉None值
        chart_files = {k: v for k, v in chart_files.items() if v is not None}

        logger.info("\n" + "="*60)
        logger.info(f"图表生成完成！共生成 {len(chart_files)} 个图表")
        logger.info("="*60)

        for name, path in chart_files.items():
            logger.info(f"  - {name}: {path}")

        return chart_files


def main():
    """主函数 - 示例用法"""
    import glob

    # 获取项目根目录
    project_root = Path(__file__).parent.parent

    # 查找最新的清洗数据文件
    data_files = glob.glob(str(project_root / 'data/processed/test_cleaned_jobs.csv'))
    if not data_files:
        data_files = glob.glob(str(project_root / 'data/processed/cleaned_jobs_*.csv'))

    if not data_files:
        logger.error("未找到清洗后的数据文件")
        logger.info("请先运行数据清洗模块生成数据")
        return

    # 使用文件
    data_file = data_files[0]
    logger.info(f"使用数据文件: {data_file}")

    # 创建可视化器
    output_dir = project_root / 'data/visualizations'
    visualizer = JobDataVisualizer(data_file, output_dir=output_dir)

    # 加载数据
    visualizer.load_data()

    # 生成所有图表
    visualizer.generate_all_charts()


if __name__ == '__main__':
    main()
