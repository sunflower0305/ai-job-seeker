# 爬虫模块使用说明

## 概述

本模块提供了两个招聘网站的爬虫：
- **Boss直聘** (boss_spider.py)
- **智联招聘** (zhilian_spider.py)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行爬虫

#### 方式1：使用主程序（推荐）

```bash
# 爬取所有网站（默认：北京、上海、深圳、杭州，Python、Java等职位，每个2页）
python scripts/crawlers/run_crawler.py

# 只爬取Boss直聘
python scripts/crawlers/run_crawler.py --spider boss

# 只爬取智联招聘
python scripts/crawlers/run_crawler.py --spider zhilian

# 自定义城市和关键词
python scripts/crawlers/run_crawler.py --cities 北京 上海 --keywords Python Java --pages 3

# 查看帮助
python scripts/crawlers/run_crawler.py --help
```

#### 方式2：单独运行某个爬虫

```bash
# 运行Boss直聘爬虫
python -m crawler.boss_spider

# 运行智联招聘爬虫
python -m crawler.zhilian_spider
```

### 3. 数据输出

爬取的数据会自动保存到 `data/raw/` 目录：
- `boss_jobs_YYYYMMDD_HHMMSS.json` - Boss直聘数据
- `zhilian_jobs_YYYYMMDD_HHMMSS.json` - 智联招聘数据
- `all_jobs_YYYYMMDD_HHMMSS.json` - 合并后的数据

## 数据格式

每条职位数据包含以下字段：

```json
{
  "job_title": "Python开发工程师",
  "company_name": "某科技公司",
  "salary_min": 15000,
  "salary_max": 25000,
  "salary_months": 12,
  "city": "北京",
  "experience": "3-5年",
  "education": "本科",
  "company_size": "100-499人",
  "company_type": "民营企业",
  "industry": "互联网",
  "job_description": "职位描述...",
  "job_tags": "五险一金,年终奖",
  "welfare": "弹性工作,节日福利",
  "source": "Boss直聘",
  "url": "https://...",
  "publish_time": "2024-01-15 10:30:00",
  "crawl_time": "2024-01-15 15:20:30"
}
```

## 配置说明

在 `config/config.py` 中可以修改以下配置：

### 目标城市
```python
TARGET_CITIES = [
    '北京', '上海', '广州', '深圳', '杭州',
    '成都', '武汉', '南京', '西安', '重庆'
]
```

### 目标职位
```python
TARGET_JOBS = [
    'Python', 'Java', 'Web前端', '数据分析',
    '算法工程师', '产品经理', 'UI设计'
]
```

### 爬虫参数
```python
SPIDER_CONFIG = {
    'delay_range': (1, 3),  # 请求延时范围（秒）
    'max_retry': 3,         # 最大重试次数
    'timeout': 30,          # 请求超时时间
}
```

## API使用示例

### Boss直聘爬虫

```python
from crawler.boss_spider import BossSpider

# 创建爬虫实例
spider = BossSpider()

# 爬取单个城市和关键词
spider.crawl_by_city_and_keyword('北京', 'Python', max_pages=3)

# 批量爬取
spider.crawl_all(
    cities=['北京', '上海'],
    keywords=['Python', 'Java'],
    max_pages=2
)

# 保存数据
spider.save_to_json('my_data.json')

# 获取统计信息
stats = spider.get_statistics()
print(stats)
```

### 智联招聘爬虫

```python
from crawler.zhilian_spider import ZhilianSpider

spider = ZhilianSpider()
spider.crawl_all(
    cities=['深圳', '杭州'],
    keywords=['数据分析', 'Web前端'],
    max_pages=2
)
spider.save_to_json()
```

## 工具函数

`utils.py` 提供了以下工具函数：

### 1. 获取随机请求头
```python
from crawler.utils import spider_utils

headers = spider_utils.get_random_headers()
```

### 2. 解析薪资
```python
min_sal, max_sal, months = spider_utils.parse_salary("10k-15k·13薪")
# 返回: (10000, 15000, 13)
```

### 3. 标准化城市名称
```python
city = spider_utils.standardize_city("北京市")
# 返回: "北京"
```

### 4. 标准化工作经验
```python
exp = spider_utils.standardize_experience("1-3年经验")
# 返回: "1-3年"
```

### 5. 标准化学历
```python
edu = spider_utils.standardize_education("本科及以上")
# 返回: "本科"
```

## 注意事项

### 1. 反爬策略
- 程序已内置随机延时（1-3秒）
- 使用随机User-Agent
- 建议不要频繁大量爬取

### 2. 网站变化
- 招聘网站可能更新页面结构或API
- 如果爬虫失败，需要更新解析逻辑

### 3. 数据质量
- 部分职位可能薪资为"面议"，会解析为None
- 建议定期爬取，保持数据新鲜度

### 4. 法律合规
- 仅用于学习和研究目的
- 请遵守网站的robots.txt协议
- 不要用于商业用途

## 故障排查

### 问题1：请求失败/超时
- 检查网络连接
- 增加延时时间
- 检查目标网站是否可访问

### 问题2：解析数据为空
- 网站可能更新了API或页面结构
- 检查浏览器开发者工具，更新API地址

### 问题3：城市编码错误
- 在爬虫类的 `_get_city_code()` 方法中添加对应城市编码

## 下一步

爬取数据后，可以进行：
1. 数据清洗 - 使用 `data_process/cleaner.py`
2. 数据存储 - 导入MySQL数据库
3. 数据分析 - 使用 `data_process/analyzer.py`
