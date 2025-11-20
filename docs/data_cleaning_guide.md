# 数据清洗模块使用指南

## 概述

数据清洗模块提供了全面的招聘数据清洗和验证功能，包括：

- **缺失值处理**：删除或填充缺失数据
- **重复数据去除**：基于职位和公司的智能去重
- **异常值处理**：使用IQR方法检测和删除异常薪资数据
- **数据标准化**：城市、学历、经验等字段的标准化
- **文本清洗**：去除HTML标签、特殊字符、URL等
- **技能标签标准化**：自动识别和标准化技术技能标签
- **技能提取**：从职位描述中提取技术关键词
- **技能分类**：将技能分为编程语言、框架、数据库等类别
- **数据验证**：全面的数据质量检查

## 快速开始

### 基本用法

```python
from data_process.cleaner import DataCleaner

# 1. 创建清洗器
cleaner = DataCleaner('data/raw/jobs.json')

# 2. 加载数据
cleaner.load_data()

# 3. 执行清洗
df = cleaner.clean()

# 4. 保存结果
cleaner.save_cleaned_data('data/processed/cleaned_jobs')
```

### 运行示例

```bash
# 方法1：使用主程序（自动查找最新数据）
cd /home/leyang/workplace/bishe/data_process
python3 cleaner.py

# 方法2：使用完整流程测试
python3 test_full_pipeline.py
```

## 详细功能说明

### 1. 数据加载

```python
cleaner = DataCleaner('data/raw/jobs.json')
df = cleaner.load_data()
```

支持的数据格式：JSON（数组格式）

必需字段：
- `job_title`: 职位标题
- `company_name`: 公司名称
- `salary_min`: 最低薪资
- `salary_max`: 最高薪资

### 2. 分步清洗

如果需要更细粒度的控制，可以单独调用各个清洗步骤：

```python
# 加载数据
cleaner.load_data()

# 处理缺失值
cleaner.handle_missing_values()

# 去除重复
cleaner.remove_duplicates()

# 处理异常值
cleaner.handle_outliers()

# 标准化数据
cleaner.standardize_data()

# 清理文本字段
cleaner.clean_text_fields()

# 从描述中提取技能
cleaner.extract_skills_from_description()

# 技能分类
cleaner.categorize_skills()

# 生成质量报告
report = cleaner.generate_quality_report()
```

### 3. 数据验证

使用独立的验证器检查数据质量：

```python
from data_process.cleaner import DataValidator

# 创建验证器
validator = DataValidator(df)

# 执行验证
report = validator.validate_all()

# 检查验证结果
if report['is_valid']:
    print("数据验证通过！")
else:
    print(f"发现 {report['error_count']} 个错误")
    print(f"发现 {report['warning_count']} 个警告")
```

## 清洗规则

### 缺失值处理

- **必填字段**：职位标题、公司名称、薪资范围缺失的记录会被删除
- **可选字段**：使用默认值填充
  - 城市 → "未知"
  - 经验 → "不限"
  - 学历 → "不限"
  - 公司规模/类型/行业 → "未知"

### 异常值检测

1. **基本范围检查**：
   - 最低薪资：0 - 100,000 元/月
   - 最高薪资：最低薪资 - 200,000 元/月

2. **IQR方法**：
   - 使用3倍IQR检测统计异常值
   - 自动删除超出合理范围的数据

### 数据标准化

#### 城市名称
- 去除"市"、"省"后缀
- 统一格式（北京市 → 北京）

#### 学历要求
- 博士 → "博士"
- 硕士/研究生 → "硕士"
- 本科/学士 → "本科"
- 大专/专科 → "大专"
- 高中/中专 → "高中"
- 其他 → "不限"

#### 工作经验
- 应届/不限 → "不限"
- 5-10年 → "5-10年"
- 3-5年 → "3-5年"
- 1-3年 → "1-3年"
- 1年以下 → "1年以下"
- 10年以上 → "10年以上"

### 技能标签标准化

支持100+常见技术标签的自动标准化：

```python
# 标准化映射示例
python → Python
java → Java
javascript/js → JavaScript
react/reactjs → React
mysql → MySQL
docker → Docker
k8s → Kubernetes
```

### 技能分类

自动将技能分为以下类别：
- `skills_languages`: 编程语言（Python, Java, JavaScript等）
- `skills_web_frameworks`: Web框架（Django, Flask, React, Vue等）
- `skills_databases`: 数据库（MySQL, MongoDB, Redis等）
- `skills_big_data`: 大数据（Hadoop, Spark, Kafka等）
- `skills_ml_ai`: 机器学习/AI（TensorFlow, PyTorch, Pandas等）
- `skills_devops`: DevOps（Docker, Kubernetes, AWS, Jenkins等）
- `skills_mobile`: 移动开发（Android, iOS, Flutter等）

## 输出文件

清洗完成后会生成以下文件：

1. **CSV文件**：`cleaned_jobs_YYYYMMDD_HHMMSS.csv`
   - 适合Excel打开和数据分析

2. **JSON文件**：`cleaned_jobs_YYYYMMDD_HHMMSS.json`
   - 适合程序读取

3. **质量报告**：`cleaned_jobs_YYYYMMDD_HHMMSS_report.json`
   - 包含详细的清洗统计信息

## 质量报告示例

```json
{
  "original_count": 500,
  "final_count": 309,
  "removed_count": 191,
  "removal_rate": "38.20%",
  "fields_count": 25,
  "salary_stats": {
    "min": 4000,
    "max": 35000,
    "avg_min": 12500,
    "avg_max": 18500,
    "median_avg": 15000
  },
  "city_distribution": {
    "北京": 85,
    "上海": 72,
    "深圳": 58,
    "杭州": 35
  }
}
```

## 测试

### 运行单元测试

```bash
cd /home/leyang/workplace/bishe/data_process
python3 test_cleaner.py -v
```

### 运行完整流程测试

```bash
python3 test_full_pipeline.py
```

## 注意事项

1. **数据备份**：清洗前请确保原始数据已备份
2. **内存使用**：大数据集（>100万条）可能需要较多内存
3. **中文支持**：文件保存使用UTF-8编码，确保正确显示中文
4. **日志级别**：可通过修改 `logging.basicConfig` 调整日志详细程度

## 性能优化建议

- 对于大型数据集，考虑分批处理
- 可以选择性执行清洗步骤以提高速度
- 技能提取较耗时，如不需要可跳过该步骤

## 故障排除

### 常见问题

**Q: 提示"请先加载数据"错误**
A: 确保在调用清洗方法前先执行 `load_data()`

**Q: 清洗后数据量大幅减少**
A: 检查原始数据质量，可能存在大量缺失值或异常值

**Q: 技能标签未被正确识别**
A: 检查 `SKILL_MAPPING` 字典，可以添加自定义映射

**Q: 编码错误**
A: 确保输入文件使用UTF-8编码

## 扩展开发

### 添加自定义技能映射

```python
# 在 DataCleaner 类中添加
DataCleaner.SKILL_MAPPING['自定义标签'] = '标准名称'
```

### 自定义验证规则

```python
# 继承 DataValidator 类
class CustomValidator(DataValidator):
    def validate_custom_rule(self):
        # 添加自定义验证逻辑
        pass
```

## 版本信息

- 版本：1.0.0
- 最后更新：2025-11-20
- Python要求：3.8+
- 依赖包：pandas, numpy

## 联系和支持

如有问题或建议，请查看项目文档或提交issue。
