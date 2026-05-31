#!/usr/bin/env python3
"""
完整的数据清洗流程测试
"""

import sys
import os
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = Path(__file__).resolve().parents[1]

from cleaner import DataCleaner, DataValidator
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_full_pipeline():
    """测试完整的清洗流程"""

    # 使用模拟数据
    input_file = PROJECT_ROOT / "data/raw/mock_jobs.json"

    if not os.path.exists(input_file):
        logger.error(f"数据文件不存在: {input_file}")
        return

    logger.info("="*80)
    logger.info("开始测试完整的数据清洗流程")
    logger.info("="*80)

    # 1. 创建清洗器
    cleaner = DataCleaner(input_file)

    # 2. 加载数据
    cleaner.load_data()

    # 3. 执行清洗
    df = cleaner.clean()

    # 4. 数据验证
    logger.info("\n" + "="*80)
    logger.info("开始数据验证")
    logger.info("="*80)

    validator = DataValidator(df)
    validation_report = validator.validate_all()

    # 5. 保存清洗后的数据
    output_file = PROJECT_ROOT / "data/processed/test_cleaned_jobs"
    cleaner.save_cleaned_data(output_file)

    # 6. 打印汇总信息
    logger.info("\n" + "="*80)
    logger.info("清洗流程汇总")
    logger.info("="*80)
    logger.info(f"原始数据: {cleaner.original_count} 条")
    logger.info(f"清洗后数据: {len(df)} 条")
    logger.info(f"删除数据: {cleaner.original_count - len(df)} 条")

    if validation_report['is_valid']:
        logger.info("\n✓ 数据质量验证通过！")
    else:
        logger.warning(f"\n⚠ 发现 {validation_report['error_count']} 个错误")

    # 7. 显示一些示例数据
    logger.info("\n" + "="*80)
    logger.info("示例数据（前3条）")
    logger.info("="*80)

    for idx, row in df.head(3).iterrows():
        logger.info(f"\n记录 {idx + 1}:")
        logger.info(f"  职位: {row['job_title']}")
        logger.info(f"  公司: {row['company_name']}")
        logger.info(f"  薪资: {row['salary_min']}-{row['salary_max']} 元/月 × {row['salary_months']}月")
        logger.info(f"  城市: {row['city']}")
        logger.info(f"  经验: {row['experience']}")
        logger.info(f"  学历: {row['education']}")
        if 'job_tags' in row and row['job_tags']:
            logger.info(f"  技能: {row['job_tags']}")
        if 'skills_languages' in row and row['skills_languages']:
            logger.info(f"  编程语言: {row['skills_languages']}")
        if 'skills_web_frameworks' in row and row['skills_web_frameworks']:
            logger.info(f"  Web框架: {row['skills_web_frameworks']}")

    logger.info("\n" + "="*80)
    logger.info("测试完成！")
    logger.info("="*80)


if __name__ == '__main__':
    test_full_pipeline()
