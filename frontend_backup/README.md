# 招聘数据分析与职位推荐系统 - 前端使用指南

## 项目概述

完整的招聘数据分析与职位推荐Web应用，集成机器学习模型，提供智能职位推荐和薪资预测功能。

## 系统架构

```
招聘数据分析与职位推荐系统
├── 后端 (Django + Django REST Framework)
│   ├── 用户认证 (Token Authentication)
│   ├── 职位管理 API
│   ├── 机器学习API (推荐 + 预测)
│   └── 数据库 (SQLite)
│
├── 前端 (HTML + CSS + JavaScript)
│   ├── 首页 (index.html)
│   ├── 职位列表 (jobs.html)
│   ├── 智能推荐 (recommend.html)
│   ├── 薪资预测 (predict.html)
│   ├── 用户登录 (login.html)
│   └── 用户注册 (register.html)
│
└── 机器学习模块
    ├── 职位推荐 (TF-IDF + 余弦相似度)
    └── 薪资预测 (随机森林回归)
```

## 快速开始

### 1. 启动Django服务器

```bash
cd /home/leyang/workplace/bishe
python3 manage.py runserver 8000
```

### 2. 访问前端页面

在浏览器中打开以下页面：

- **首页**: `file:///home/leyang/workplace/bishe/frontend/templates/index.html`
- **职位列表**: `file:///home/leyang/workplace/bishe/frontend/templates/jobs.html`
- **智能推荐**: `file:///home/leyang/workplace/bishe/frontend/templates/recommend.html`
- **薪资预测**: `file:///home/leyang/workplace/bishe/frontend/templates/predict.html`
- **用户登录**: `file:///home/leyang/workplace/bishe/frontend/templates/login.html`
- **用户注册**: `file:///home/leyang/workplace/bishe/frontend/templates/register.html`

## 功能说明

### 1. 首页 (index.html)

**功能**:
- 系统介绍和功能展示
- 实时统计数据（职位数量、平均薪资、模型准确度）
- 快速导航到各功能模块

**使用方法**:
- 直接打开即可查看系统概览
- 点击功能卡片跳转到对应模块

### 2. 用户注册 (register.html)

**功能**:
- 创建新用户账号
- 支持求职者和招聘者角色选择

**使用方法**:
1. 填写用户名、邮箱、密码
2. 选择用户类型（求职者/招聘者）
3. 可选填写手机号
4. 点击"注册"按钮
5. 注册成功后自动跳转到首页

### 3. 用户登录 (login.html)

**功能**:
- 用户身份验证
- 获取访问Token

**使用方法**:
1. 输入用户名和密码
2. 点击"登录"按钮
3. 登录成功后跳转到首页
4. 登录状态会保存在浏览器中

### 4. 职位列表 (jobs.html)

**功能**:
- 浏览所有职位
- 多维度筛选（城市、学历、经验、薪资）
- 关键词搜索
- 分页显示

**使用方法**:
1. 在搜索框输入关键词搜索
2. 使用下拉菜单筛选条件
3. 点击"搜索"按钮应用筛选
4. 点击"重置"清空所有筛选条件
5. 使用分页按钮浏览更多职位

**筛选选项**:
- 城市: 北京、上海、广州、深圳等
- 学历: 不限、大专、本科、硕士、博士
- 经验: 不限、1年以下、1-3年、3-5年等
- 薪资范围: 自定义最低/最高薪资
- 排序: 最新发布、薪资最高、薪资最低

### 5. 智能推荐 (recommend.html)

**功能**:
- 基于用户画像的职位推荐
- 使用TF-IDF + 余弦相似度算法
- 显示匹配度评分

**使用方法**:
1. 添加技能标签（在输入框中输入后按回车）
2. 选择工作经验
3. 选择学历要求
4. 输入期望城市
5. 输入期望行业
6. 设置推荐数量（1-50）
7. 点击"获取推荐"按钮

**推荐结果**:
- 职位名称和公司
- 薪资范围
- 城市、学历、经验要求
- 匹配度评分（0-100%）
- 技能标签

### 6. 薪资预测 (predict.html)

**功能**:
- 预测职位薪资水平
- 使用随机森林回归模型
- 提供薪资范围和置信区间

**使用方法**:
1. 选择工作城市 *
2. 选择学历 *
3. 选择工作经验 *
4. 输入行业（默认: 互联网）
5. 选择公司规模
6. 选择公司类型
7. 输入薪资月数（12-18）
8. 添加技能标签（可选）
9. 点击"开始预测"按钮

**预测结果**:
- 预测月薪
- 薪资下限和上限（80%置信区间）
- 预估年薪
- 置信度
- 模型性能指标

## API端点

### 用户相关
- `POST /api/users/register/` - 用户注册
- `POST /api/users/login/` - 用户登录
- `POST /api/users/logout/` - 用户登出
- `GET /api/users/me/` - 获取当前用户信息
- `GET/PUT /api/users/me/profile/` - 用户档案

### 职位相关
- `GET /api/jobs/jobs/` - 职位列表（支持筛选）
- `GET /api/jobs/jobs/{id}/` - 职位详情
- `POST /api/jobs/jobs/{id}/apply/` - 申请职位
- `POST/DELETE /api/jobs/jobs/{id}/collect/` - 收藏/取消收藏

### 机器学习
- `POST /api/ml/recommend/` - 职位推荐
- `POST /api/ml/predict-salary/` - 薪资预测
- `GET /api/ml/model-status/` - 模型状态

## 系统特性

### 技术栈
- **后端**: Django 5.2, Django REST Framework
- **前端**: 原生HTML/CSS/JavaScript（无框架依赖）
- **数据库**: SQLite
- **机器学习**: scikit-learn, jieba

### 机器学习模型

**职位推荐系统**:
- 算法: TF-IDF + 余弦相似度
- 特征: 500个TF-IDF特征
- 数据: 309个职位样本
- 中文分词: Jieba

**薪资预测系统**:
- 算法: 随机森林回归
- 特征: 15维特征
- 性能: MAE 2,985元, R² 0.5144
- 预测: 提供薪资范围和置信区间

### 设计特点
- **响应式设计**: 适配各种屏幕尺寸
- **现代UI**: 渐变背景、卡片设计、平滑动画
- **用户友好**: 清晰的表单验证和错误提示
- **实时反馈**: 加载动画和操作提示

## 常见问题

### Q: 为什么推荐结果为空？
A: 可能是筛选条件过于严格（如城市、经验要求），尝试放宽条件或减少技能标签。

### Q: 薪资预测不准确？
A: 确保输入的城市、学历、经验在训练数据范围内。模型基于309个样本训练，覆盖主要城市和常见职位。

### Q: 无法登录？
A: 确保Django服务器正在运行（localhost:8000），检查用户名和密码是否正确。

### Q: 页面样式异常？
A: 确保CSS文件路径正确，浏览器支持现代CSS特性。

## 项目结构

```
bishe/
├── frontend/                    # 前端目录
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css       # 主样式文件
│   │   └── js/
│   │       └── api.js          # API客户端
│   └── templates/
│       ├── index.html          # 首页
│       ├── jobs.html           # 职位列表
│       ├── recommend.html      # 智能推荐
│       ├── predict.html        # 薪资预测
│       ├── login.html          # 登录
│       └── register.html       # 注册
│
├── job_platform/               # Django项目配置
├── jobs/                       # 职位应用
├── users/                      # 用户应用
├── recommendations/            # 推荐应用
├── ml_models/                  # 机器学习模块
└── data/                       # 数据目录
    ├── models/                 # 训练好的模型
    └── processed/              # 清洗后的数据
```

## 性能指标

- **职位推荐**: < 500ms响应时间
- **薪资预测**: < 100ms响应时间
- **职位列表**: 分页加载，每页20条
- **模型准确度**: R² 0.5144

## 更新日志

**v1.0.0** (2025-11-20)
- ✅ 完整的前端界面
- ✅ 用户认证系统
- ✅ 职位搜索和筛选
- ✅ 智能推荐功能
- ✅ 薪资预测功能
- ✅ 响应式设计
- ✅ RESTful API集成

## 联系方式

如有问题或建议，请查看项目文档或提交issue。
