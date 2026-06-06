[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/sunflower0305/ai-job-seeker)
[![Cloudflare](https://img.shields.io/badge/Cloudflare-F38020?logo=cloudflare&logoColor=white)](https://job.zhangleyang.com)

# AI 求职助手

把求职里最常见的几件事放到同一个系统里：上传简历、分析岗位、推荐职位、预测薪资、优化简历、导出文档。
项目演示：[https://job.zhangleyang.com](https://job.zhangleyang.com)
博客介绍：https://blog.zhangleyang.com/2026-05-31-aainct

## 项目简介

本系统是一个完整的招聘数据分析解决方案，通过爬虫技术获取招聘网站数据，利用数据分析和机器学习技术，为求职者提供薪资分析、职位推荐、薪资预测等功能。

## 核心功能

### 1. 数据获取

- 爬取主流招聘网站职位数据（智联招聘/前程无忧/Boss 直聘）
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

- **职位推荐**：基于 TF-IDF 和余弦相似度的推荐算法
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
- **UI 框架**：Bootstrap

## 项目结构

```
ai-job-seeker/
├── manage.py              # Django 管理入口
├── start.sh / stop.sh     # 本地启动与停止脚本
├── job_platform/          # Django 项目配置
├── jobs/                  # 职位、分析、文档生成相关应用
├── users/                 # 用户、权限、访问日志相关应用
├── recommendations/       # 推荐相关应用
├── crawler/               # 爬虫核心模块
├── data_process/          # 数据清洗、分析、可视化模块
├── ml_models/             # 机器学习模型
├── frontend/              # Next.js 前端
├── scripts/
│   ├── crawlers/          # 爬虫运行、Cookie、页面诊断脚本
│   └── data/              # 数据导入、清理、检查、初始化脚本
├── tests/manual/          # 手动/集成验证脚本
├── docs/
│   ├── guides/            # 使用和功能指南
│   └── reports/           # 阶段性报告和修复记录
├── reports/               # JSON 等运行报告输出
├── runtime/               # PID 等运行时文件
├── data/                  # 原始数据、处理后数据、模型和图表
├── config/                # 配置文件
└── requirements.txt
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

创建 MySQL 数据库：

```sql
CREATE DATABASE job_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

配置数据库连接（config/config.py）

### 5. 数据迁移

```bash
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
python scripts/crawlers/run_crawler.py
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

### 数据导入和检查

```bash
python scripts/data/import_jobs_data.py
python scripts/data/check_data_quality.py
```

## 开发计划

- [x] 项目初始化
- [x] 数据爬虫实现
- [x] 数据清洗与存储
- [x] 数据分析模块
- [x] Django Web 框架搭建
- [x] 数据可视化实现
- [x] 推荐算法实现
- [x] 薪资预测模型
- [x] 用户系统开发
- [x] 前端页面开发
- [x] 系统测试与优化
