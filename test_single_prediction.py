#!/usr/bin/env python
"""
测试单个预测的详细信息
"""

import sys
from pathlib import Path
import numpy as np

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ml_models.predictor import SalaryPredictor

def main():
    print("="*60)
    print("详细分析预测置信度")
    print("="*60)

    # 加载模型
    predictor = SalaryPredictor(model_dir='data/models')
    model_file = project_root / 'data/models/salary_predictor.pkl'

    if not model_file.exists():
        print(f"❌ 模型文件不存在: {model_file}")
        return

    predictor.load_model(str(model_file))
    print("✓ 模型加载成功")
    print(f"  随机森林树的数量: {len(predictor.model.estimators_)}\n")

    # 用户输入测试
    print("请输入职位信息进行测试：")
    job_features = {
        'city': input("城市 (默认: 北京): ").strip() or '北京',
        'education': input("学历 (默认: 本科): ").strip() or '本科',
        'experience': input("经验 (默认: 3-5年): ").strip() or '3-5年',
        'industry': input("行业 (默认: 互联网): ").strip() or '互联网',
        'company_size': input("公司规模 (默认: 100-499人): ").strip() or '100-499人',
        'company_type': input("公司类型 (默认: 民营): ").strip() or '民营',
        'salary_months': int(input("薪资月数 (默认: 13): ").strip() or 13),
        'skills': input("技能 (用逗号分隔, 默认: Python,Django): ").strip().split(',') or ['Python', 'Django']
    }

    print("\n" + "="*60)
    print("预测分析")
    print("="*60)

    # 预测
    result = predictor.predict_with_confidence(job_features)

    # 获取所有树的预测
    X = predictor._prepare_single_feature(job_features)
    tree_predictions = np.array([tree.predict(X)[0] for tree in predictor.model.estimators_])

    print(f"\n1. 基础统计信息:")
    print(f"   平均预测薪资: {result['predicted_salary']:,.0f} 元/月")
    print(f"   标准差: {result['std']:,.0f} 元")
    print(f"   最小预测: {tree_predictions.min():,.0f} 元")
    print(f"   最大预测: {tree_predictions.max():,.0f} 元")
    print(f"   预测范围: {tree_predictions.max() - tree_predictions.min():,.0f} 元")

    print(f"\n2. 变异系数 (CV):")
    print(f"   CV = 标准差 / 平均值 = {result['std']:.0f} / {result['predicted_salary']:.0f} = {result['cv']:.3f}")
    print(f"   CV 含义: 预测值的离散程度，越小越一致")

    print(f"\n3. 置信度计算:")
    print(f"   公式: confidence = 1 / (1 + exp(15 * (cv - 0.25)))")
    print(f"   当前置信度: {result['confidence']:.1%}")

    print(f"\n4. 置信度参考标准:")
    print(f"   CV < 0.15 → 置信度 > 85% (高)")
    print(f"   CV = 0.25 → 置信度 ≈ 50% (中)")
    print(f"   CV = 0.35 → 置信度 ≈ 20% (低)")
    print(f"   CV > 0.45 → 置信度 < 5% (极低)")
    print(f"   你的 CV = {result['cv']:.3f}")

    print(f"\n5. 树的预测分布:")
    percentiles = [10, 25, 50, 75, 90]
    print(f"   {'百分位':<10} {'薪资':<10}")
    print(f"   {'-'*20}")
    for p in percentiles:
        val = np.percentile(tree_predictions, p)
        print(f"   P{p:<8} {val:>10,.0f} 元")

    print(f"\n6. 置信度低的可能原因:")
    if result['cv'] > 0.35:
        print(f"   ❌ CV值很高 ({result['cv']:.3f})，说明:")
        print(f"      - 不同决策树对这个职位给出了差异很大的预测")
        print(f"      - 可能这个职位特征组合在训练数据中较少见")
        print(f"      - 模型对此类职位的预测不够稳定")

    # 分析特征
    print(f"\n7. 输入特征分析:")
    print(f"   城市: {job_features['city']}")
    print(f"   学历: {job_features['education']}")
    print(f"   经验: {job_features['experience']}")
    print(f"   行业: {job_features['industry']}")
    print(f"   技能数: {len(job_features['skills'])}")

    print(f"\n8. 改进建议:")
    print(f"   - 如果是常见职位组合，考虑增加训练数据量")
    print(f"   - 如果是特殊职位组合，置信度低是正常的")
    print(f"   - 可以调整置信度计算公式，使结果更符合预期")

if __name__ == '__main__':
    main()
