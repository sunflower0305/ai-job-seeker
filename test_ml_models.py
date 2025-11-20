#!/usr/bin/env python3
"""
机器学习模块完整测试
演示职位推荐和薪资预测功能
"""

import sys
import os
from pathlib import Path
import logging

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'ml_models'))

from ml_models.recommender import JobRecommender
from ml_models.predictor import SalaryPredictor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_ml_models():
    """测试机器学习模型"""

    logger.info("\n" + "="*80)
    logger.info("机器学习模块测试 - 职位推荐 + 薪资预测")
    logger.info("="*80)

    # 数据文件
    data_file = project_root / 'data/processed/test_cleaned_jobs.csv'

    if not data_file.exists():
        logger.error(f"数据文件不存在: {data_file}")
        return

    # ===== 第一部分：职位推荐系统 =====
    logger.info("\n【第一部分】职位推荐系统")
    logger.info("-" * 80)

    recommender = JobRecommender()
    recommender.load_data(str(data_file))
    recommender.train(max_features=500)

    # 场景1：基于职位的推荐
    logger.info("\n场景1：为已有职位推荐相似职位")
    job_id = 10
    recommendations = recommender.recommend_by_job_id(job_id, top_n=3, return_scores=True)

    original_job = recommender.df.iloc[job_id]
    logger.info(f"\n原职位:")
    logger.info(f"  标题: {original_job['job_title']}")
    logger.info(f"  公司: {original_job['company_name']}")
    logger.info(f"  城市: {original_job['city']}")
    logger.info(f"  薪资: {original_job['salary_min']}-{original_job['salary_max']} 元/月")

    logger.info(f"\n推荐的3个相似职位:")
    for i, rec in enumerate(recommendations, 1):
        logger.info(f"\n  {i}. {rec['job_title']} - {rec['company_name']}")
        logger.info(f"     城市: {rec['city']}, 薪资: {rec['salary_min']}-{rec['salary_max']} 元/月")
        logger.info(f"     相似度: {rec['similarity_score']:.3f}")

    # 场景2：基于用户画像的推荐
    logger.info("\n场景2：根据求职者画像推荐职位")

    user_profiles = [
        {
            'name': 'Python后端工程师',
            'profile': {
                'skills': ['Python', 'Django', 'FastAPI', 'PostgreSQL', 'Redis', 'Docker'],
                'experience': '3-5年',
                'education': '本科',
                'preferred_city': '上海',
                'preferred_industry': '互联网'
            }
        },
        {
            'name': 'Java全栈工程师',
            'profile': {
                'skills': ['Java', 'Spring Boot', 'Vue', 'MySQL', 'Redis'],
                'experience': '5-10年',
                'education': '硕士',
                'preferred_city': '北京',
                'preferred_industry': '金融'
            }
        }
    ]

    for user in user_profiles:
        logger.info(f"\n求职者: {user['name']}")
        profile = user['profile']
        logger.info(f"  技能: {', '.join(profile['skills'])}")
        logger.info(f"  经验: {profile['experience']}")
        logger.info(f"  学历: {profile['education']}")
        logger.info(f"  期望城市: {profile['preferred_city']}")

        recommendations = recommender.recommend_by_profile(profile, top_n=3)

        logger.info(f"\n  推荐职位:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"    {i}. {rec['job_title']} - {rec['company_name']}")
            logger.info(f"       薪资: {rec['salary_min']}-{rec['salary_max']} 元/月, 相似度: {rec['similarity_score']:.3f}")

    # 保存推荐模型
    recommender.save_model()

    # ===== 第二部分：薪资预测系统 =====
    logger.info("\n【第二部分】薪资预测系统")
    logger.info("-" * 80)

    predictor = SalaryPredictor()
    predictor.load_data(str(data_file))
    metrics = predictor.train()

    logger.info(f"\n模型性能总结:")
    logger.info(f"  测试集 MAE: {metrics['test']['mae']:.0f} 元")
    logger.info(f"  测试集 R²: {metrics['test']['r2']:.4f}")
    logger.info(f"  交叉验证 MAE: {metrics['cv_mae']:.0f} 元")

    # 薪资预测场景
    logger.info("\n场景：为不同职位预测薪资")

    test_cases = [
        {
            'title': 'Python高级工程师 (北京, 互联网, 3-5年经验)',
            'features': {
                'city': '北京',
                'education': '本科',
                'experience': '3-5年',
                'industry': '互联网',
                'company_size': '500-999人',
                'company_type': '民营',
                'salary_months': 13,
                'skills': ['Python', 'Django', 'MySQL', 'Redis', 'Docker']
            }
        },
        {
            'title': 'Java架构师 (上海, 金融, 10年以上经验)',
            'features': {
                'city': '上海',
                'education': '硕士',
                'experience': '10年以上',
                'industry': '金融',
                'company_size': '10000人以上',
                'company_type': '上市公司',
                'salary_months': 16,
                'skills': ['Java', 'Spring', 'MySQL', 'Redis', 'Kafka', 'Kubernetes']
            }
        },
        {
            'title': '前端开发工程师 (深圳, 电商, 1-3年经验)',
            'features': {
                'city': '深圳',
                'education': '本科',
                'experience': '1-3年',
                'industry': '电子商务',
                'company_size': '100-499人',
                'company_type': '民营',
                'salary_months': 12,
                'skills': ['Vue', 'React', 'JavaScript', 'HTML', 'CSS']
            }
        },
        {
            'title': '算法工程师 (杭州, AI, 3-5年经验)',
            'features': {
                'city': '杭州',
                'education': '博士',
                'experience': '3-5年',
                'industry': '人工智能',
                'company_size': '1000-9999人',
                'company_type': '民营',
                'salary_months': 14,
                'skills': ['Python', 'TensorFlow', 'PyTorch', 'NLP']
            }
        }
    ]

    for case in test_cases:
        logger.info(f"\n{case['title']}")
        features = case['features']

        # 预测薪资
        avg_salary = predictor.predict(features)
        avg, min_sal, max_sal = predictor.predict_salary_range(features, confidence=0.8)

        logger.info(f"  预测平均薪资: {avg_salary:.0f} 元/月")
        logger.info(f"  预测薪资范围: {min_sal:.0f} - {max_sal:.0f} 元/月 (80%置信区间)")
        logger.info(f"  预估年薪: {avg * features['salary_months'] / 10000:.1f} 万元")

    # 保存预测模型
    predictor.save_model()

    # ===== 综合应用场景 =====
    logger.info("\n【综合应用】职位推荐 + 薪资评估")
    logger.info("-" * 80)

    # 为求职者推荐职位并预测薪资
    user_profile = {
        'skills': ['Python', 'Django', 'MySQL', 'Redis'],
        'experience': '3-5年',
        'education': '本科',
        'preferred_city': '北京',
        'preferred_industry': '互联网'
    }

    logger.info(f"\n求职者画像:")
    logger.info(f"  技能: {', '.join(user_profile['skills'])}")
    logger.info(f"  经验: {user_profile['experience']}")
    logger.info(f"  期望城市: {user_profile['preferred_city']}")

    # 推荐职位
    recommendations = recommender.recommend_by_profile(user_profile, top_n=5)

    logger.info(f"\n为您推荐以下职位:")
    for i, rec in enumerate(recommendations[:5], 1):
        logger.info(f"\n  {i}. {rec['job_title']} - {rec['company_name']}")
        logger.info(f"     实际薪资: {rec['salary_min']}-{rec['salary_max']} 元/月")

        # 使用预测模型评估薪资合理性
        predicted_salary = predictor.predict({
            'city': rec.get('city', '北京'),
            'education': rec.get('education', '本科'),
            'experience': rec.get('experience', '3-5年'),
            'industry': rec.get('industry', '互联网'),
            'company_size': rec.get('company_size', '100-499人'),
            'company_type': rec.get('company_type', '民营'),
            'salary_months': rec.get('salary_months', 12),
            'skills': user_profile['skills']
        })

        actual_avg = (rec['salary_min'] + rec['salary_max']) / 2
        diff_pct = ((actual_avg - predicted_salary) / predicted_salary) * 100

        logger.info(f"     市场参考薪资: {predicted_salary:.0f} 元/月")
        if diff_pct > 10:
            logger.info(f"     薪资评价: 高于市场 {diff_pct:.1f}% ⭐")
        elif diff_pct < -10:
            logger.info(f"     薪资评价: 低于市场 {abs(diff_pct):.1f}%")
        else:
            logger.info(f"     薪资评价: 符合市场预期")

        logger.info(f"     推荐匹配度: {rec['similarity_score']:.1%}")

    # ===== 完成 =====
    logger.info("\n" + "="*80)
    logger.info("测试完成！")
    logger.info("="*80)

    summary = {
        'recommender': {
            'model_file': 'data/models/job_recommender.pkl',
            'features_count': len(recommender.feature_names),
            'jobs_count': len(recommender.df)
        },
        'predictor': {
            'model_file': 'data/models/salary_predictor.pkl',
            'test_mae': metrics['test']['mae'],
            'test_r2': metrics['test']['r2'],
            'features_count': len(predictor.feature_columns)
        }
    }

    logger.info(f"\n模型信息:")
    logger.info(f"  推荐系统: {summary['recommender']['jobs_count']} 个职位, "
                f"{summary['recommender']['features_count']} 个特征")
    logger.info(f"  预测系统: MAE={summary['predictor']['test_mae']:.0f}元, "
                f"R²={summary['predictor']['test_r2']:.4f}")

    return summary


def print_system_info():
    """打印系统信息"""
    import sklearn
    import jieba

    logger.info("\n系统环境:")
    logger.info(f"  Python版本: {sys.version.split()[0]}")
    logger.info(f"  Scikit-learn版本: {sklearn.__version__}")
    logger.info(f"  Jieba版本: {jieba.__version__}")


if __name__ == '__main__':
    try:
        # 打印系统信息
        print_system_info()

        # 执行测试
        summary = test_ml_models()

        logger.info("\n✓ 所有测试通过！")

    except Exception as e:
        logger.error(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
