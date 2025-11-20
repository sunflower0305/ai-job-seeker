"""
项目配置文件
包含数据库连接、爬虫配置等
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',  # 请修改为实际密码
    'database': 'job_analysis',
    'charset': 'utf8mb4'
}

# SQLAlchemy 连接字符串
SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
    f"?charset={DATABASE_CONFIG['charset']}"
)

# 数据存储路径
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
MODELS_DIR = os.path.join(DATA_DIR, 'models')

# 日志配置
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# 爬虫配置
SPIDER_CONFIG = {
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    ],
    'delay_range': (1, 3),  # 请求延时范围（秒）
    'max_retry': 3,          # 最大重试次数
    'timeout': 30,           # 请求超时时间
}

# 目标城市列表
TARGET_CITIES = [
    '北京', '上海', '广州', '深圳', '杭州',
    '成都', '武汉', '南京', '西安', '重庆'
]

# 目标职位关键词
TARGET_JOBS = [
    'Python', 'Java', 'Web前端', '数据分析',
    '算法工程师', '产品经理', 'UI设计'
]

# 机器学习配置
ML_CONFIG = {
    'test_size': 0.2,        # 测试集比例
    'random_state': 42,      # 随机种子
    'n_estimators': 100,     # 随机森林树的数量
    'max_features': 10,      # TF-IDF最大特征数
}
