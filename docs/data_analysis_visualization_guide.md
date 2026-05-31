# 数据分析和可视化模块使用指南

## 概述

数据分析和可视化模块提供了全面的招聘数据分析和图表生成功能，包括：

### 数据分析模块 (analyzer.py)
- **基础统计分析**：职位数量、公司数量、城市分布等
- **薪资分析**：按城市、学历、经验、行业等多维度分析
- **技能需求分析**：热门技能统计、技能分类、技能与薪资关系
- **职位分布分析**：城市、学历、经验、行业、公司规模分布
- **相关性分析**：数值字段相关性矩阵

### 数据可视化模块 (visualizer.py)
- **薪资分布直方图**：展示整体薪资分布情况
- **城市薪资对比图**：横向对比各城市平均薪资
- **学历薪资关系图**：箱线图 + 条形图展示学历与薪资关系
- **经验薪资关系图**：折线图展示经验与薪资的增长趋势
- **技能词云图**：直观展示热门技能
- **热门技能Top N**：条形图展示最受欢迎的技能
- **行业分布饼图**：展示各行业职位占比

## 快速开始

### 1. 数据分析

```python
from data_process.analyzer import JobDataAnalyzer

# 创建分析器
analyzer = JobDataAnalyzer('data/processed/cleaned_jobs.csv')

# 加载数据
analyzer.load_data()

# 执行所有分析
results = analyzer.analyze_all()

# 保存分析报告
analyzer.save_report('data/processed/analysis_report.json')
```

### 2. 数据可视化

```python
from data_process.visualizer import JobDataVisualizer

# 创建可视化器
visualizer = JobDataVisualizer(
    'data/processed/cleaned_jobs.csv',
    output_dir='data/visualizations'
)

# 加载数据
visualizer.load_data()

# 生成所有图表
chart_files = visualizer.generate_all_charts()
```

### 3. 一键运行

```bash
# 数据分析
cd /Users/joe/ai/ai-job-seeker/data_process
python3 analyzer.py

# 数据可视化
python3 visualizer.py
```

## 详细功能说明

### 数据分析模块

#### 1. 基础统计分析

```python
stats = analyzer.get_basic_statistics()
```

返回数据：
- 职位总数
- 公司总数
- 城市总数
- 数据字段数量
- 数据时间范围
- 数据来源统计

#### 2. 薪资分析

```python
salary_analysis = analyzer.analyze_salary()
```

分析维度：
- **整体统计**：均值、中位数、标准差、最小值、最大值、四分位数
- **按城市**：各城市平均薪资、中位数、职位数量
- **按学历**：不同学历要求的薪资分布
- **按经验**：不同工作经验的薪资水平
- **按行业**：各行业薪资对比

返回示例：
```json
{
  "overall": {
    "mean": 12964,
    "median": 11500,
    "min": 3000,
    "max": 34000
  },
  "by_city": {
    "上海": {"mean": 17926, "count": 34},
    "北京": {"mean": 15000, "count": 33}
  },
  "by_education": {
    "博士": {"mean": 16448, "count": 67},
    "硕士": {"mean": 14857, "count": 56}
  }
}
```

#### 3. 技能需求分析

```python
skills_analysis = analyzer.analyze_skills()
```

分析内容：
- **热门技能Top 50**：统计出现频次最高的技能
- **技能分类统计**：按技能类别（语言、框架、数据库等）统计
- **技能与薪资关系**：分析掌握特定技能的平均薪资

返回示例：
```json
{
  "top_skills": [
    {"skill": "Vue", "count": 82},
    {"skill": "Docker", "count": 81},
    {"skill": "Java", "count": 78}
  ],
  "skill_salary": {
    "Flask": {"count": 53, "avg_salary": 13925},
    "Git": {"count": 72, "avg_salary": 13771}
  }
}
```

#### 4. 职位分布分析

```python
distribution = analyzer.analyze_job_distribution()
```

统计内容：
- 城市分布（Top 20）
- 学历要求分布
- 经验要求分布
- 公司规模分布
- 行业分布（Top 15）

#### 5. 相关性分析

```python
correlations = analyzer.analyze_correlations()
```

计算数值字段间的相关系数矩阵，例如：
- salary_min 与 salary_max 的相关性
- salary_avg 与 salary_months 的相关性

### 数据可视化模块

#### 1. 薪资分布直方图

```python
visualizer.plot_salary_distribution()
```

特点：
- 30个分bin的直方图
- 标注平均值和中位数线
- 网格线辅助阅读

#### 2. 城市薪资对比图

```python
visualizer.plot_salary_by_city(top_n=10)
```

特点：
- 横向条形图便于对比
- 显示平均薪资和职位数量
- 仅展示职位数≥5的城市
- 按薪资降序排列

#### 3. 学历薪资关系图

```python
visualizer.plot_salary_by_education()
```

特点：
- 双图布局（箱线图 + 条形图）
- 箱线图显示薪资分布范围
- 条形图显示平均薪资

#### 4. 经验薪资关系图

```python
visualizer.plot_salary_by_experience()
```

特点：
- 折线图展示薪资随经验增长趋势
- 填充区域显示薪资范围
- 数值标签清晰标注

#### 5. 技能词云图

```python
visualizer.plot_skills_wordcloud(max_words=100)
```

特点：
- 词的大小代表出现频率
- Viridis配色方案
- 美观直观

#### 6. 热门技能Top N

```python
visualizer.plot_top_skills(top_n=20)
```

特点：
- 横向条形图
- 显示数量和占比
- 按频次降序排列

#### 7. 行业分布饼图

```python
visualizer.plot_industry_distribution(top_n=10)
```

特点：
- 饼图展示占比
- 自动合并"其他"类别
- 百分比标注

## 输出文件

### 分析报告 (JSON格式)

文件命名：`analysis_report_YYYYMMDD_HHMMSS.json`

结构：
```json
{
  "metadata": {
    "generated_at": "2025-11-20T14:08:27",
    "total_records": 309
  },
  "analysis": {
    "basic_statistics": {...},
    "salary_analysis": {...},
    "skills_analysis": {...},
    "distribution": {...},
    "correlations": {...}
  }
}
```

### 可视化图表 (PNG格式)

存储位置：`data/visualizations/`

生成文件：
1. `salary_distribution.png` - 薪资分布图
2. `salary_by_city.png` - 城市薪资对比图
3. `salary_by_education.png` - 学历薪资关系图
4. `salary_by_experience.png` - 经验薪资关系图
5. `skills_wordcloud.png` - 技能词云图
6. `top_20_skills.png` - 热门技能Top 20
7. `industry_distribution.png` - 行业分布图

## 实际应用示例

### 示例1：薪资市场调研

```python
from data_process.analyzer import JobDataAnalyzer

# 加载数据
analyzer = JobDataAnalyzer('cleaned_jobs.csv')
analyzer.load_data()

# 分析薪资
salary_analysis = analyzer.analyze_salary()

# 获取指定城市的薪资数据
beijing_salary = salary_analysis['by_city']['北京']
print(f"北京平均薪资: {beijing_salary['mean']}元/月")

# 获取指定学历的薪资数据
master_salary = salary_analysis['by_education']['硕士']
print(f"硕士学历平均薪资: {master_salary['mean']}元/月")
```

### 示例2：技能需求分析

```python
from data_process.analyzer import JobDataAnalyzer

analyzer = JobDataAnalyzer('cleaned_jobs.csv')
analyzer.load_data()

# 分析技能需求
skills_analysis = analyzer.analyze_skills()

# 查看最热门的10个技能
for skill_info in skills_analysis['top_skills'][:10]:
    skill = skill_info['skill']
    count = skill_info['count']
    print(f"{skill}: {count}个职位")

# 查看薪资最高的技能
for skill, data in list(skills_analysis['skill_salary'].items())[:10]:
    print(f"{skill}: 平均薪资 {data['avg_salary']}元/月")
```

### 示例3：生成分析报告

```python
from data_process.analyzer import JobDataAnalyzer
from data_process.visualizer import JobDataVisualizer

# 数据分析
analyzer = JobDataAnalyzer('cleaned_jobs.csv')
analyzer.load_data()
analyzer.analyze_all()
analyzer.save_report('report.json')

# 数据可视化
visualizer = JobDataVisualizer('cleaned_jobs.csv')
visualizer.load_data()
visualizer.generate_all_charts()

print("分析报告和可视化图表已生成！")
```

## 测试运行

### 运行测试脚本

```bash
# 测试数据分析
cd /Users/joe/ai/ai-job-seeker/data_process
python3 test_analyzer.py

# 测试数据可视化
python3 visualizer.py
```

### 测试结果

**数据分析输出示例：**
```
============================================================
薪资分析
============================================================
平均薪资: 12964 元/月
中位数薪资: 11500 元/月
薪资范围: 3000 - 34000 元/月

薪资最高的5个城市:
  上海: 平均 17926 元/月 (34 个职位)
  北京: 平均 15000 元/月 (33 个职位)
  ...

最热门的20个技能:
   1. Vue                 :   82 ( 26.5%)
   2. Docker              :   81 ( 26.2%)
   3. C++                 :   81 ( 26.2%)
  ...
```

**可视化输出示例：**
```
图表生成完成！共生成 7 个图表
  - salary_distribution: salary_distribution.png
  - salary_by_city: salary_by_city.png
  - salary_by_education: salary_by_education.png
  ...
```

## 性能优化建议

1. **大数据集处理**：
   - 对于>10000条数据，建议分批分析
   - 可选择性执行部分分析功能

2. **图表生成**：
   - 调整DPI参数控制图片质量和大小
   - 减少top_n参数值加快生成速度

3. **内存管理**：
   - 及时关闭matplotlib图表：`plt.close()`
   - 使用完数据后删除DataFrame：`del df`

## 故障排除

### 常见问题

**Q: 中文显示为方框**
A: 这是字体警告，不影响功能。如需完美显示中文，可安装中文字体包。

**Q: 生成的图表为空**
A: 检查数据文件中是否包含相应字段，如`job_tags`、`salary_avg`等。

**Q: 分析报告没有某些维度的数据**
A: 确认清洗后的数据包含对应字段且数据有效。

**Q: 技能词云图不显示**
A: 确保安装了wordcloud库：`pip3 install wordcloud`

## 扩展开发

### 添加自定义分析

```python
# 继承JobDataAnalyzer类
from data_process.analyzer import JobDataAnalyzer

class CustomAnalyzer(JobDataAnalyzer):
    def analyze_custom_metric(self):
        """自定义分析方法"""
        # 添加自定义分析逻辑
        pass
```

### 添加自定义图表

```python
# 继承JobDataVisualizer类
from data_process.visualizer import JobDataVisualizer

class CustomVisualizer(JobDataVisualizer):
    def plot_custom_chart(self):
        """自定义图表方法"""
        # 添加自定义图表逻辑
        pass
```

## 版本信息

- 版本：1.0.0
- 最后更新：2025-11-20
- Python要求：3.8+
- 依赖包：
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - wordcloud

## 参考资料

- [Matplotlib官方文档](https://matplotlib.org/)
- [Seaborn官方文档](https://seaborn.pydata.org/)
- [Pandas官方文档](https://pandas.pydata.org/)
- [WordCloud文档](https://amueller.github.io/word_cloud/)

## 联系和支持

如有问题或建议，请查看项目文档或提交issue。
