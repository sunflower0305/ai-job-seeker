# 机器学习模块使用指南

## 概述

机器学习模块提供了两个核心功能：
1. **职位推荐系统**：基于TF-IDF和余弦相似度的智能推荐
2. **薪资预测系统**：基于随机森林的薪资预测模型

## 模块一：职位推荐系统

### 功能特性

- **基于职位的推荐**：根据职位特征找到相似职位
- **基于用户画像的推荐**：根据求职者技能和偏好推荐匹配职位
- **推荐解释**：提供推荐理由和匹配度评分
- **多维度特征**：综合考虑职位标题、描述、技能、行业等

### 核心技术

- **TF-IDF**：文本特征提取
- **Jieba分词**：中文文本分词
- **余弦相似度**：计算职位相似度
- **N-gram**：1-gram和2-gram特征

### 快速开始

```python
from ml_models.recommender import JobRecommender

# 1. 创建推荐器
recommender = JobRecommender()

# 2. 加载数据
recommender.load_data('data/processed/cleaned_jobs.csv')

# 3. 训练模型
recommender.train(max_features=500)

# 4. 保存模型
recommender.save_model()
```

### 使用场景

#### 场景1：基于职位ID推荐

```python
# 为职位ID=10推荐5个相似职位
recommendations = recommender.recommend_by_job_id(
    job_id=10,
    top_n=5,
    return_scores=True
)

for rec in recommendations:
    print(f"{rec['job_title']} - 相似度: {rec['similarity_score']:.3f}")
```

#### 场景2：基于用户画像推荐

```python
# 定义用户画像
user_profile = {
    'skills': ['Python', 'Django', 'MySQL', 'Redis'],
    'experience': '3-5年',
    'education': '本科',
    'preferred_city': '北京',
    'preferred_industry': '互联网'
}

# 获取推荐
recommendations = recommender.recommend_by_profile(user_profile, top_n=10)

for rec in recommendations:
    print(f"{rec['job_title']} - {rec['company_name']}")
    print(f"  薪资: {rec['salary_min']}-{rec['salary_max']} 元/月")
    print(f"  匹配度: {rec['similarity_score']:.1%}")
```

#### 场景3：获取推荐解释

```python
# 解释为什么推荐这个职位
explanation = recommender.get_recommendation_explanation(
    job_id=10,
    recommended_job_id=20
)

print(f"相似度: {explanation['similarity_score']:.3f}")
print(f"共同关键词: {', '.join(explanation['common_keywords'][:5])}")
```

### API参考

#### JobRecommender类

**初始化参数：**
- `model_dir`: 模型保存目录（默认: 'data/models'）

**主要方法：**

1. `load_data(data_source)`
   - 参数：数据源（文件路径或DataFrame）
   - 返回：加载的DataFrame

2. `train(max_features=500)`
   - 参数：TF-IDF最大特征数
   - 功能：训练推荐模型

3. `recommend_by_job_id(job_id, top_n=10, return_scores=False)`
   - 参数：
     - job_id: 职位索引ID
     - top_n: 推荐数量
     - return_scores: 是否返回相似度分数
   - 返回：推荐职位列表

4. `recommend_by_profile(user_profile, top_n=10)`
   - 参数：
     - user_profile: 用户画像字典
     - top_n: 推荐数量
   - 返回：推荐职位列表

5. `save_model(filename=None)` / `load_model(filename=None)`
   - 功能：保存/加载模型

### 推荐算法原理

1. **特征构建**：
   - 职位标题（权重×3）
   - 职位描述（权重×1）
   - 技能标签（权重×2）
   - 行业、公司类型、福利（权重×1）

2. **文本处理**：
   - Jieba中文分词
   - 停用词过滤
   - TF-IDF向量化

3. **相似度计算**：
   - 使用余弦相似度
   - 范围：0（完全不相似）到1（完全相似）

4. **个性化过滤**：
   - 城市偏好过滤
   - 经验要求匹配
   - 技能匹配优先

## 模块二：薪资预测系统

### 功能特性

- **薪资预测**：预测职位的平均薪资
- **薪资范围估计**：提供置信区间
- **特征重要性分析**：识别影响薪资的关键因素
- **模型评估**：提供MAE、RMSE、R²等指标

### 核心技术

- **随机森林回归**：集成学习算法
- **Label Encoding**：类别特征编码
- **交叉验证**：5折交叉验证
- **特征工程**：技能数量、技能分类统计

### 快速开始

```python
from ml_models.predictor import SalaryPredictor

# 1. 创建预测器
predictor = SalaryPredictor()

# 2. 加载数据
predictor.load_data('data/processed/cleaned_jobs.csv')

# 3. 训练模型
metrics = predictor.train()

# 4. 保存模型
predictor.save_model()
```

### 使用场景

#### 场景1：预测单个职位薪资

```python
job_features = {
    'city': '北京',
    'education': '本科',
    'experience': '3-5年',
    'industry': '互联网',
    'company_size': '500-999人',
    'company_type': '民营',
    'salary_months': 13,
    'skills': ['Python', 'Django', 'MySQL', 'Redis']
}

# 预测平均薪资
predicted_salary = predictor.predict(job_features)
print(f"预测薪资: {predicted_salary:.0f} 元/月")

# 预测薪资范围（80%置信区间）
avg, min_sal, max_sal = predictor.predict_salary_range(
    job_features,
    confidence=0.8
)
print(f"薪资范围: {min_sal:.0f} - {max_sal:.0f} 元/月")
print(f"年薪估计: {avg * 13 / 10000:.1f} 万元")
```

#### 场景2：批量预测

```python
jobs = [
    {...},  # 职位1特征
    {...},  # 职位2特征
    {...},  # 职位3特征
]

for job in jobs:
    salary = predictor.predict(job)
    print(f"{job['city']} - {job['experience']}: {salary:.0f} 元/月")
```

#### 场景3：查看特征重要性

```python
# 获取模型评估指标
metrics = predictor.train()

# 打印特征重要性
for feature, importance in sorted(
    metrics['feature_importance'].items(),
    key=lambda x: x[1],
    reverse=True
)[:10]:
    print(f"{feature}: {importance:.4f}")
```

### API参考

#### SalaryPredictor类

**初始化参数：**
- `model_dir`: 模型保存目录（默认: 'data/models'）

**主要方法：**

1. `load_data(data_source)`
   - 参数：数据源（文件路径或DataFrame）
   - 返回：加载的DataFrame

2. `prepare_features()`
   - 功能：准备特征工程
   - 返回：特征列名列表

3. `train(target='salary_avg', test_size=0.2, random_state=42)`
   - 参数：
     - target: 目标变量
     - test_size: 测试集比例
     - random_state: 随机种子
   - 返回：评估指标字典

4. `predict(job_features)`
   - 参数：职位特征字典
   - 返回：预测的平均薪资（float）

5. `predict_salary_range(job_features, confidence=0.8)`
   - 参数：
     - job_features: 职位特征
     - confidence: 置信水平
   - 返回：(平均薪资, 最低薪资, 最高薪资)

6. `save_model(filename=None)` / `load_model(filename=None)`
   - 功能：保存/加载模型

### 模型性能

**测试结果（基于309条数据）：**
- **MAE**: 2,985元
- **RMSE**: 3,849元
- **R²**: 0.5144
- **交叉验证MAE**: 3,046 ± 344元

### 特征说明

**类别特征：**
- city: 城市
- education: 学历要求
- experience: 工作经验
- industry: 行业
- company_size: 公司规模
- company_type: 公司类型

**数值特征：**
- salary_months: 薪资月数
- skills_count: 技能总数
- skills_*_count: 各类别技能数量

## 综合应用场景

### 场景：智能求职助手

结合推荐和预测功能，为求职者提供全面的职位建议：

```python
from ml_models.recommender import JobRecommender
from ml_models.predictor import SalaryPredictor

# 初始化
recommender = JobRecommender()
recommender.load_data('cleaned_jobs.csv')
recommender.train()

predictor = SalaryPredictor()
predictor.load_data('cleaned_jobs.csv')
predictor.train()

# 用户画像
user_profile = {
    'skills': ['Python', 'Django', 'MySQL'],
    'experience': '3-5年',
    'education': '本科',
    'preferred_city': '北京',
    'preferred_industry': '互联网'
}

# 获取推荐
recommendations = recommender.recommend_by_profile(user_profile, top_n=10)

# 为每个推荐职位评估薪资
for rec in recommendations:
    # 实际薪资
    actual_avg = (rec['salary_min'] + rec['salary_max']) / 2

    # 预测薪资
    predicted_salary = predictor.predict({
        'city': rec['city'],
        'education': rec['education'],
        'experience': rec['experience'],
        'industry': rec['industry'],
        'company_size': rec['company_size'],
        'company_type': rec['company_type'],
        'salary_months': rec['salary_months'],
        'skills': user_profile['skills']
    })

    # 薪资评估
    diff_pct = ((actual_avg - predicted_salary) / predicted_salary) * 100

    print(f"\n{rec['job_title']} - {rec['company_name']}")
    print(f"  实际薪资: {rec['salary_min']}-{rec['salary_max']} 元/月")
    print(f"  市场参考: {predicted_salary:.0f} 元/月")
    print(f"  匹配度: {rec['similarity_score']:.1%}")

    if diff_pct > 10:
        print(f"  💰 薪资高于市场 {diff_pct:.1f}%")
    elif diff_pct < -10:
        print(f"  ⚠️  薪资低于市场 {abs(diff_pct):.1f}%")
    else:
        print(f"  ✓ 薪资符合市场")
```

## 模型文件

训练后的模型保存在 `data/models/` 目录：
- `job_recommender.pkl`: 推荐系统模型
- `salary_predictor.pkl`: 薪资预测模型

模型包含：
- 训练好的算法
- 特征编码器
- 特征名称列表
- 训练数据引用

## 性能优化建议

### 推荐系统

1. **增加特征维度**：
   ```python
   recommender.train(max_features=1000)  # 增加特征数
   ```

2. **调整权重**：
   修改 `build_feature_text` 方法中的重复次数

3. **自定义停用词**：
   ```python
   recommender.stop_words.update(['你的', '停用词'])
   ```

### 预测系统

1. **调整模型参数**：
   ```python
   from sklearn.ensemble import RandomForestRegressor

   predictor.model = RandomForestRegressor(
       n_estimators=200,  # 增加树的数量
       max_depth=15,      # 增加树的深度
       min_samples_split=3
   )
   ```

2. **添加更多特征**：
   - 公司成立年限
   - 地理位置细分
   - 技能组合特征

3. **超参数调优**：
   ```python
   from sklearn.model_selection import GridSearchCV

   param_grid = {
       'n_estimators': [100, 200, 300],
       'max_depth': [10, 15, 20],
       'min_samples_split': [2, 5, 10]
   }

   grid_search = GridSearchCV(
       RandomForestRegressor(),
       param_grid,
       cv=5,
       scoring='neg_mean_absolute_error'
   )
   ```

## 故障排除

### 常见问题

**Q: 推荐结果为空**
A: 检查用户画像的城市和经验要求是否过于严格，尝试放宽条件。

**Q: 预测薪资异常高或异常低**
A: 检查输入特征是否正确，特别是 city、experience 等是否在训练数据的范围内。

**Q: 模型加载失败**
A: 确保模型文件存在且与当前代码版本兼容。

**Q: 中文分词效果不佳**
A: 可以添加自定义词典：
```python
import jieba
jieba.load_userdict('custom_dict.txt')
```

## 版本信息

- 版本：1.0.0
- 最后更新：2025-11-20
- Python要求：3.8+
- 依赖包：
  - scikit-learn >= 1.0
  - jieba >= 0.42
  - pandas >= 1.3
  - numpy >= 1.21
  - scipy >= 1.7

## 参考资料

- [Scikit-learn文档](https://scikit-learn.org/)
- [Jieba分词](https://github.com/fxsjy/jieba)
- [TF-IDF原理](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- [随机森林算法](https://en.wikipedia.org/wiki/Random_forest)

## 联系和支持

如有问题或建议，请查看项目文档或提交issue。
