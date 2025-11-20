#!/usr/bin/env python3
"""
数据分析测试脚本
"""

import sys
import os
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from analyzer import JobDataAnalyzer
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_analyzer():
    """测试数据分析器"""

    # 使用测试数据
    data_file = "/home/leyang/workplace/bishe/data/processed/test_cleaned_jobs.csv"

    if not os.path.exists(data_file):
        logger.error(f"数据文件不存在: {data_file}")
        return

    logger.info("="*80)
    logger.info("开始测试数据分析模块")
    logger.info("="*80)

    # 创建分析器
    analyzer = JobDataAnalyzer(data_file)

    # 加载数据
    analyzer.load_data()

    # 执行所有分析
    results = analyzer.analyze_all()

    # 保存报告
    report_file = "/home/leyang/workplace/bishe/data/processed/test_analysis_report.json"
    analyzer.save_report(report_file)

    logger.info("\n" + "="*80)
    logger.info("测试完成！")
    logger.info("="*80)

    return results


if __name__ == '__main__':
    test_analyzer()
