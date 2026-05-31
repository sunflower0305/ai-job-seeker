"""
数据库初始化脚本
用于创建数据库和数据表
"""

from _bootstrap import PROJECT_ROOT

import pymysql
from database.models import db
from config.config import DATABASE_CONFIG


def create_database():
    """创建数据库"""
    try:
        # 连接MySQL（不指定数据库）
        connection = pymysql.connect(
            host=DATABASE_CONFIG['host'],
            port=DATABASE_CONFIG['port'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            charset=DATABASE_CONFIG['charset']
        )

        cursor = connection.cursor()

        # 检查数据库是否存在
        cursor.execute(f"SHOW DATABASES LIKE '{DATABASE_CONFIG['database']}'")
        result = cursor.fetchone()

        if not result:
            # 创建数据库
            cursor.execute(
                f"CREATE DATABASE {DATABASE_CONFIG['database']} "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            print(f"✓ 数据库 '{DATABASE_CONFIG['database']}' 创建成功！")
        else:
            print(f"✓ 数据库 '{DATABASE_CONFIG['database']}' 已存在")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"✗ 数据库创建失败: {e}")
        return False

    return True


def create_tables():
    """创建数据表"""
    try:
        db.create_tables()
        print("✓ 数据表创建成功！")
        return True
    except Exception as e:
        print(f"✗ 数据表创建失败: {e}")
        return False


def main():
    """主函数"""
    print("="*50)
    print("开始初始化数据库...")
    print("="*50)

    # 创建数据库
    if not create_database():
        return

    # 创建数据表
    if not create_tables():
        return

    print("="*50)
    print("数据库初始化完成！")
    print("="*50)


if __name__ == '__main__':
    main()
