#!/usr/bin/env python3
"""
完整数据处理流程演示
展示从数据清洗到分析再到可视化的完整流程
"""

from _bootstrap import PROJECT_ROOT

import sys
import os
from pathlib import Path
import logging

# 添加项目路径
project_root = PROJECT_ROOT

from data_process.cleaner import DataCleaner, DataValidator
from data_process.analyzer import JobDataAnalyzer
from data_process.visualizer import JobDataVisualizer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def complete_data_pipeline():
    """完整的数据处理管道"""

    logger.info("\n" + "="*80)
    logger.info("招聘数据分析系统 - 完整流程演示")
    logger.info("="*80)

    # ===== 步骤1: 数据清洗 =====
    logger.info("\n【步骤1/3】数据清洗")
    logger.info("-" * 80)

    # 使用模拟数据
    raw_data_file = project_root / 'data/raw/mock_jobs.json'

    if not raw_data_file.exists():
        logger.error(f"原始数据文件不存在: {raw_data_file}")
        return

    # 创建清洗器
    cleaner = DataCleaner(str(raw_data_file))
    cleaner.load_data()

    # 执行清洗
    cleaned_df = cleaner.clean()

    # 数据验证
    validator = DataValidator(cleaned_df)
    validation_report = validator.validate_all()

    if not validation_report['is_valid']:
        logger.warning(f"数据验证发现 {validation_report['error_count']} 个错误")

    # 保存清洗后的数据
    cleaned_file = project_root / 'data/processed/demo_cleaned_jobs'
    cleaner.save_cleaned_data(str(cleaned_file))

    logger.info(f"\n清洗完成:")
    logger.info(f"  原始数据: {cleaner.original_count} 条")
    logger.info(f"  清洗后: {len(cleaned_df)} 条")
    logger.info(f"  删除: {cleaner.original_count - len(cleaned_df)} 条")

    # ===== 步骤2: 数据分析 =====
    logger.info("\n【步骤2/3】数据分析")
    logger.info("-" * 80)

    # 创建分析器（使用清洗后的DataFrame）
    analyzer = JobDataAnalyzer(cleaned_df)
    analyzer.load_data()

    # 执行所有分析
    analysis_results = analyzer.analyze_all()

    # 保存分析报告
    report_file = project_root / 'data/processed/demo_analysis_report.json'
    analyzer.save_report(str(report_file))

    # 打印关键分析结果
    logger.info(f"\n分析结果摘要:")

    if 'salary_analysis' in analysis_results:
        salary = analysis_results['salary_analysis']
        if 'overall' in salary:
            logger.info(f"  平均薪资: {salary['overall']['mean']:.0f} 元/月")
            logger.info(f"  薪资范围: {salary['overall']['min']:.0f} - {salary['overall']['max']:.0f} 元/月")

    if 'skills_analysis' in analysis_results:
        skills = analysis_results['skills_analysis']
        if 'top_skills' in skills and skills['top_skills']:
            logger.info(f"  最热门技能: {skills['top_skills'][0]['skill']} ({skills['top_skills'][0]['count']}个职位)")

    if 'distribution' in analysis_results:
        dist = analysis_results['distribution']
        if 'by_city' in dist:
            top_city = list(dist['by_city'].items())[0]
            logger.info(f"  职位最多城市: {top_city[0]} ({top_city[1]}个职位)")

    # ===== 步骤3: 数据可视化 =====
    logger.info("\n【步骤3/3】数据可视化")
    logger.info("-" * 80)

    # 创建可视化器
    viz_output_dir = project_root / 'data/visualizations/demo'
    visualizer = JobDataVisualizer(cleaned_df, output_dir=str(viz_output_dir))
    visualizer.load_data()

    # 生成所有图表
    chart_files = visualizer.generate_all_charts()

    logger.info(f"\n生成的图表:")
    for name, path in chart_files.items():
        logger.info(f"  - {name}: {Path(path).name}")

    # ===== 流程完成 =====
    logger.info("\n" + "="*80)
    logger.info("完整流程执行成功！")
    logger.info("="*80)

    logger.info(f"\n输出文件:")
    logger.info(f"  1. 清洗数据: {cleaned_file}.csv / {cleaned_file}.json")
    logger.info(f"  2. 分析报告: {report_file}")
    logger.info(f"  3. 可视化图表: {viz_output_dir}/ (共{len(chart_files)}个)")

    # 生成总结报告
    summary = {
        'data_cleaning': {
            'original_records': cleaner.original_count,
            'cleaned_records': len(cleaned_df),
            'removed_records': cleaner.original_count - len(cleaned_df),
            'validation_errors': validation_report['error_count'],
            'validation_warnings': validation_report['warning_count']
        },
        'data_analysis': {
            'total_companies': analysis_results.get('basic_statistics', {}).get('total_companies', 0),
            'total_cities': analysis_results.get('basic_statistics', {}).get('total_cities', 0),
            'avg_salary': analysis_results.get('salary_analysis', {}).get('overall', {}).get('mean', 0)
        },
        'data_visualization': {
            'charts_generated': len(chart_files),
            'chart_names': list(chart_files.keys())
        }
    }

    return summary


def print_system_info():
    """打印系统信息"""
    import pandas as pd
    import matplotlib
    import seaborn as sns

    logger.info("\n系统环境:")
    logger.info(f"  Python版本: {sys.version.split()[0]}")
    logger.info(f"  Pandas版本: {pd.__version__}")
    logger.info(f"  Matplotlib版本: {matplotlib.__version__}")
    logger.info(f"  Seaborn版本: {sns.__version__}")


if __name__ == '__main__':
    try:
        # 打印系统信息
        print_system_info()

        # 执行完整流程
        summary = complete_data_pipeline()

        # 打印流程总结
        if summary:
            logger.info("\n" + "="*80)
            logger.info("流程总结")
            logger.info("="*80)
            logger.info(f"\n数据清洗:")
            logger.info(f"  - 处理记录: {summary['data_cleaning']['original_records']} → {summary['data_cleaning']['cleaned_records']}")
            logger.info(f"  - 验证错误: {summary['data_cleaning']['validation_errors']}")

            logger.info(f"\n数据分析:")
            logger.info(f"  - 公司数量: {summary['data_analysis']['total_companies']}")
            logger.info(f"  - 城市数量: {summary['data_analysis']['total_cities']}")
            logger.info(f"  - 平均薪资: {summary['data_analysis']['avg_salary']:.0f} 元/月")

            logger.info(f"\n数据可视化:")
            logger.info(f"  - 生成图表: {summary['data_visualization']['charts_generated']} 个")

        logger.info("\n✓ 演示完成！")

    except Exception as e:
        logger.error(f"\n✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
