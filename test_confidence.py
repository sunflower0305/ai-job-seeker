#!/usr/bin/env python
"""
测试薪资预测置信度计算
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ml_models.predictor import SalaryPredictor

def main():
    print("="*60)
    print("测试薪资预测置信度计算")
    print("="*60)

    # 加载模型
    predictor = SalaryPredictor(model_dir='data/models')
    model_file = project_root / 'data/models/salary_predictor.pkl'

    if not model_file.exists():
        print(f"❌ 模型文件不存在: {model_file}")
        return

    predictor.load_model(str(model_file))
    print("✓ 模型加载成功\n")

    # 测试不同的职位配置
    test_cases = [
        {
            'name': '高级Python工程师 - 北京',
            'features': {
                'city': '北京',
                'education': '本科',
                'experience': '5-10年',
                'industry': '互联网',
                'company_size': '1000-9999人',
                'company_type': '上市公司',
                'salary_months': 14,
                'skills': ['Python', 'Django', 'MySQL', 'Redis', 'Docker']
            }
        },
        {
            'name': '初级前端开发 - 杭州',
            'features': {
                'city': '杭州',
                'education': '大专',
                'experience': '1-3年',
                'industry': '互联网',
                'company_size': '20-99人',
                'company_type': '创业公司',
                'salary_months': 12,
                'skills': ['JavaScript', 'Vue']
            }
        },
        {
            'name': '中级Java开发 - 上海',
            'features': {
                'city': '上海',
                'education': '本科',
                'experience': '3-5年',
                'industry': '金融',
                'company_size': '500-999人',
                'company_type': '外资',
                'salary_months': 13,
                'skills': ['Java', 'Spring', 'MySQL']
            }
        },
        {
            'name': '数据科学家 - 深圳',
            'features': {
                'city': '深圳',
                'education': '硕士',
                'experience': '3-5年',
                'industry': '互联网',
                'company_size': '100-499人',
                'company_type': '民营',
                'salary_months': 15,
                'skills': ['Python', 'TensorFlow', 'SQL', 'Spark']
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {test_case['name']}")
        print("-" * 60)

        features = test_case['features']
        print(f"城市: {features['city']}")
        print(f"学历: {features['education']}")
        print(f"经验: {features['experience']}")
        print(f"行业: {features['industry']}")
        print(f"技能: {', '.join(features['skills'])}")

        try:
            # 使用新方法预测
            result = predictor.predict_with_confidence(features)

            print(f"\n预测结果:")
            print(f"  平均薪资: {result['predicted_salary']:,.0f} 元/月")
            print(f"  薪资范围: {result['salary_min']:,.0f} - {result['salary_max']:,.0f} 元/月")
            print(f"  置信度: {result['confidence']:.1%}")
            print(f"  标准差: {result['std']:,.0f} 元")
            print(f"  变异系数: {result['cv']:.3f}")

            # 年薪估算
            annual = result['predicted_salary'] * features['salary_months'] / 10000
            print(f"  预估年薪: {annual:.1f} 万元")

        except Exception as e:
            print(f"❌ 预测失败: {e}")

    print("\n" + "="*60)
    print("✓ 测试完成！")
    print("="*60)
    print("\n置信度说明:")
    print("  > 90%: 高置信度 - 模型对预测非常确定")
    print("  70-90%: 中等置信度 - 模型预测比较可靠")
    print("  < 70%: 低置信度 - 预测结果可能不太准确，需谨慎参考")

if __name__ == '__main__':
    main()
