"""
数据库模型定义
使用SQLAlchemy ORM定义数据表结构
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from config.config import SQLALCHEMY_DATABASE_URI

Base = declarative_base()


class Job(Base):
    """职位信息表"""
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_title = Column(String(200), nullable=False, comment='职位名称')
    company_name = Column(String(200), nullable=False, comment='公司名称')

    # 薪资信息
    salary_min = Column(Integer, comment='最低薪资')
    salary_max = Column(Integer, comment='最高薪资')
    salary_months = Column(Integer, default=12, comment='薪资月数')

    # 职位要求
    city = Column(String(50), comment='工作城市')
    experience = Column(String(50), comment='工作经验要求')
    education = Column(String(50), comment='学历要求')

    # 公司信息
    company_size = Column(String(50), comment='公司规模')
    company_type = Column(String(50), comment='公司类型')
    industry = Column(String(100), comment='所属行业')

    # 职位详情
    job_description = Column(Text, comment='职位描述')
    job_tags = Column(String(500), comment='职位标签')
    welfare = Column(String(500), comment='福利待遇')

    # 其他信息
    source = Column(String(50), comment='数据来源')
    url = Column(String(500), comment='职位链接')
    publish_time = Column(DateTime, comment='发布时间')
    crawl_time = Column(DateTime, default=datetime.now, comment='爬取时间')

    def __repr__(self):
        return f"<Job {self.job_title} - {self.company_name}>"


class User(Base):
    """用户表"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment='用户名')
    password = Column(String(255), nullable=False, comment='密码')
    email = Column(String(100), unique=True, comment='邮箱')
    phone = Column(String(20), comment='手机号')

    # 个人信息
    real_name = Column(String(50), comment='真实姓名')
    gender = Column(String(10), comment='性别')
    age = Column(Integer, comment='年龄')
    city = Column(String(50), comment='所在城市')
    education = Column(String(50), comment='学历')
    experience = Column(String(50), comment='工作经验')

    # 求职意向
    desired_position = Column(String(200), comment='期望职位')
    desired_salary = Column(String(50), comment='期望薪资')

    # 时间信息
    register_time = Column(DateTime, default=datetime.now, comment='注册时间')
    last_login = Column(DateTime, comment='最后登录时间')

    # 关联关系
    browse_history = relationship('BrowseHistory', back_populates='user')
    favorites = relationship('Favorite', back_populates='user')

    def __repr__(self):
        return f"<User {self.username}>"


class BrowseHistory(Base):
    """浏览历史表"""
    __tablename__ = 'browse_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    browse_time = Column(DateTime, default=datetime.now, comment='浏览时间')

    # 关联关系
    user = relationship('User', back_populates='browse_history')
    job = relationship('Job')

    def __repr__(self):
        return f"<BrowseHistory user:{self.user_id} job:{self.job_id}>"


class Favorite(Base):
    """收藏表"""
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    favorite_time = Column(DateTime, default=datetime.now, comment='收藏时间')

    # 关联关系
    user = relationship('User', back_populates='favorites')
    job = relationship('Job')

    def __repr__(self):
        return f"<Favorite user:{self.user_id} job:{self.job_id}>"


class SalaryPrediction(Base):
    """薪资预测记录表"""
    __tablename__ = 'salary_predictions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    # 输入特征
    job_type = Column(String(100), comment='职位类型')
    city = Column(String(50), comment='城市')
    education = Column(String(50), comment='学历')
    experience = Column(String(50), comment='工作经验')

    # 预测结果
    predicted_salary_min = Column(Integer, comment='预测最低薪资')
    predicted_salary_max = Column(Integer, comment='预测最高薪资')

    predict_time = Column(DateTime, default=datetime.now, comment='预测时间')

    def __repr__(self):
        return f"<SalaryPrediction {self.job_type} - {self.city}>"


# 数据库操作类
class Database:
    """数据库操作封装"""

    def __init__(self):
        self.engine = create_engine(
            SQLALCHEMY_DATABASE_URI,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600
        )
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """创建所有数据表"""
        Base.metadata.create_all(self.engine)
        print("数据表创建成功！")

    def drop_tables(self):
        """删除所有数据表"""
        Base.metadata.drop_all(self.engine)
        print("数据表删除成功！")

    def get_session(self):
        """获取数据库会话"""
        return self.Session()


# 创建数据库实例
db = Database()


if __name__ == '__main__':
    # 创建数据表
    db.create_tables()
