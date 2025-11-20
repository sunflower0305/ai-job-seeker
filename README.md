# 招聘数据分析可视化系统

基于Python的招聘数据分析可视化系统，包含数据爬取、数据分析、数据可视化、机器学习预测与推荐功能。

## 项目简介

本系统是一个完整的招聘数据分析解决方案，通过爬虫技术获取招聘网站数据，利用数据分析和机器学习技术，为求职者提供薪资分析、职位推荐、薪资预测等功能。

## 核心功能

### 1. 数据获取
- 爬取主流招聘网站职位数据（智联招聘/前程无忧/Boss直聘）
- 支持多线程/异步爬取
- 反爬策略处理

### 2. 数据清洗与分析
- 薪资数据标准化
- 缺失值和异常值处理
- 多维度统计分析（城市、学历、经验、行业等）

### 3. 数据可视化
- 城市薪资分布地图
- 薪资/学历/经验分布图表
- 技能词云图
- 行业/公司规模分析

### 4. 机器学习
- **职位推荐**：基于TF-IDF和余弦相似度的推荐算法
- **薪资预测**：使用随机森林/逻辑回归预测薪资区间

### 5. 用户系统
- 用户注册/登录
- 个人信息管理
- 浏览历史记录
- 职位收藏功能

## 技术栈

### 后端
- **框架**：Django 4.2
- **数据库**：MySQL 8.0
- **ORM**：SQLAlchemy

### 数据处理
- **爬虫**：Requests + BeautifulSoup4 + Selenium + Scrapy
- **分析**：Pandas + NumPy
- **可视化**：Matplotlib + Seaborn + WordCloud

### 机器学习
- **框架**：Scikit-learn
- **NLP**：Jieba（中文分词）
- **算法**：TF-IDF、余弦相似度、随机森林、逻辑回归

### 前端
- **基础**：HTML5 + CSS3 + JavaScript
- **图表**：ECharts
- **UI框架**：Bootstrap

## 项目结构

```
job_analysis/
├── crawler/              # 爬虫模块
│   ├── __init__.py
│   ├── boss_spider.py   # Boss直聘爬虫
│   ├── zhilian_spider.py # 智联招聘爬虫
│   └── utils.py         # 爬虫工具函数
├── data_process/        # 数据处理模块
│   ├── __init__.py
│   ├── cleaner.py      # 数据清洗
│   ├── analyzer.py     # 数据分析
│   └── visualizer.py   # 数据可视化
├── ml_models/           # 机器学习模块
│   ├── __init__.py
│   ├── recommender.py  # 职位推荐
│   └── predictor.py    # 薪资预测
├── web_app/             # Django Web应用
│   ├── manage.py
│   ├── job_system/      # 项目配置
│   └── apps/            # 应用模块
├── data/                # 数据存储
│   ├── raw/            # 原始数据
│   ├── processed/      # 处理后数据
│   └── models/         # 训练模型
├── config/              # 配置文件
│   └── config.py
├── logs/                # 日志文件
├── requirements.txt     # 依赖包
└── README.md
```

## 安装部署

### 1. 环境要求
- Python 3.8+
- MySQL 8.0+
- pip

### 2. 克隆项目
```bash
git clone <repository-url>
cd bishe
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 数据库配置
创建MySQL数据库：
```sql
CREATE DATABASE job_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

配置数据库连接（config/config.py）

### 5. 数据迁移
```bash
cd web_app
python manage.py makemigrations
python manage.py migrate
```

### 6. 运行项目
```bash
python manage.py runserver
```

访问：http://127.0.0.1:8000

## 使用说明

### 数据爬取
```bash
python crawler/boss_spider.py
```

### 数据清洗
```bash
python data_process/cleaner.py
```

### 数据分析
```bash
python data_process/analyzer.py
```

### 模型训练
```bash
python ml_models/predictor.py --train
```

## 开发计划

- [x] 项目初始化
- [ ] 数据爬虫实现
- [ ] 数据清洗与存储
- [ ] 数据分析模块
- [ ] Django Web框架搭建
- [ ] 数据可视化实现
- [ ] 推荐算法实现
- [ ] 薪资预测模型
- [ ] 用户系统开发
- [ ] 前端页面开发
- [ ] 系统测试与优化

## 作者

计算机科学与技术专业 毕业设计项目

## 许可证

MIT License
