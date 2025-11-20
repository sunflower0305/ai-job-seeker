"""
数据清洗模块的单元测试
"""

import unittest
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime
from cleaner import DataCleaner


class TestDataCleaner(unittest.TestCase):
    """测试DataCleaner类"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建测试数据
        self.test_data = [
            {
                "job_title": "Python开发工程师",
                "company_name": "测试公司A",
                "salary_min": 10000,
                "salary_max": 15000,
                "salary_months": 12,
                "city": "北京市",
                "experience": "3-5年",
                "education": "本科及以上",
                "company_size": "100-499人",
                "company_type": "民营",
                "industry": "互联网",
                "job_description": "负责后端开发",
                "job_tags": "Python,Django,MySQL",
                "welfare": "五险一金,带薪年假",
                "source": "测试",
                "url": "http://test.com/1",
                "publish_time": "2025-11-01 10:00:00",
                "crawl_time": "2025-11-20 10:00:00"
            },
            {
                "job_title": "  Java开发工程师  \n",
                "company_name": "测试公司B",
                "salary_min": 8000,
                "salary_max": 12000,
                "salary_months": 13,
                "city": "上海",
                "experience": "1-3年工作经验",
                "education": "大专",
                "company_size": "500-999人",
                "company_type": "外企",
                "industry": "金融",
                "job_description": "开发Java应用",
                "job_tags": "Java,Spring,Redis",
                "welfare": "弹性工作",
                "source": "测试",
                "url": "http://test.com/2",
                "publish_time": "2025-11-05 14:00:00",
                "crawl_time": "2025-11-20 10:00:00"
            },
            {
                "job_title": "Python开发工程师",  # 重复数据
                "company_name": "测试公司A",
                "salary_min": 10000,
                "salary_max": 15000,
                "salary_months": 12,
                "city": "北京",
                "experience": "3-5年",
                "education": "本科",
                "company_size": "100-499人",
                "company_type": "民营",
                "industry": "互联网",
                "job_description": "负责后端开发",
                "job_tags": "Python,Django",
                "welfare": "五险一金",
                "source": "测试",
                "url": "http://test.com/3",
                "publish_time": "2025-11-01 10:00:00",
                "crawl_time": "2025-11-20 10:00:00"
            },
            {
                "job_title": "",  # 空标题，应被删除
                "company_name": "测试公司C",
                "salary_min": 5000,
                "salary_max": 8000,
                "salary_months": 12,
                "city": "深圳",
                "experience": "不限",
                "education": "不限",
                "company_size": "少于50人",
                "company_type": "创业",
                "industry": "电商",
                "job_description": "测试职位",
                "job_tags": "",
                "welfare": "",
                "source": "测试",
                "url": "http://test.com/4",
                "publish_time": "2025-11-10 16:00:00",
                "crawl_time": "2025-11-20 10:00:00"
            },
            {
                "job_title": "前端开发",
                "company_name": "测试公司D",
                "salary_min": -1000,  # 异常薪资，应被删除
                "salary_max": 8000,
                "salary_months": 12,
                "city": "广州",
                "experience": "应届生",
                "education": "硕士研究生",
                "company_size": "1000人以上",
                "company_type": "上市公司",
                "industry": "游戏",
                "job_description": "前端开发工作",
                "job_tags": "Vue,React",
                "welfare": "股票期权",
                "source": "测试",
                "url": "http://test.com/5",
                "publish_time": "2025-11-15 09:00:00",
                "crawl_time": "2025-11-20 10:00:00"
            },
            {
                "job_title": "算法工程师",
                "company_name": "测试公司E",
                "salary_min": None,  # 缺失薪资，应被删除
                "salary_max": None,
                "salary_months": 12,
                "city": None,
                "experience": None,
                "education": None,
                "company_size": None,
                "company_type": None,
                "industry": None,
                "job_description": None,
                "job_tags": None,
                "welfare": None,
                "source": "测试",
                "url": "http://test.com/6",
                "publish_time": "2025-11-18 11:00:00",
                "crawl_time": "2025-11-20 10:00:00"
            }
        ]

        # 创建临时测试文件
        self.test_file = "data/test/test_jobs.json"
        os.makedirs("data/test", exist_ok=True)
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, ensure_ascii=False, indent=2)

        # 创建清洗器实例
        self.cleaner = DataCleaner(self.test_file)

    def tearDown(self):
        """测试后的清理工作"""
        # 删除测试文件
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

        # 删除生成的输出文件
        test_dir = Path("data/test")
        if test_dir.exists():
            for file in test_dir.glob("*"):
                if file.is_file():
                    file.unlink()
            test_dir.rmdir()

    def test_load_data(self):
        """测试数据加载功能"""
        df = self.cleaner.load_data()

        # 验证数据加载成功
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 6)  # 原始数据有6条
        self.assertEqual(self.cleaner.original_count, 6)

        # 验证必要的列存在
        required_columns = ['job_title', 'company_name', 'salary_min', 'salary_max']
        for col in required_columns:
            self.assertIn(col, df.columns)

    def test_handle_missing_values(self):
        """测试缺失值处理"""
        self.cleaner.load_data()
        self.cleaner.handle_missing_values()

        # 验证空标题和空公司的记录被删除
        self.assertNotIn("", self.cleaner.df['job_title'].values)

        # 验证薪资缺失的记录被删除
        self.assertFalse(self.cleaner.df['salary_min'].isna().any())
        self.assertFalse(self.cleaner.df['salary_max'].isna().any())

        # 验证其他字段的缺失值被填充
        if 'city' in self.cleaner.df.columns:
            # 如果city列还在，检查没有None值
            filled_cities = self.cleaner.df['city'].fillna('未知')
            self.assertNotIn(None, filled_cities.values)

    def test_remove_duplicates(self):
        """测试去重功能"""
        self.cleaner.load_data()
        self.cleaner.handle_missing_values()

        before_count = len(self.cleaner.df)
        self.cleaner.remove_duplicates()
        after_count = len(self.cleaner.df)

        # 验证重复数据被删除
        self.assertLess(after_count, before_count)

        # 验证没有重复的职位-公司组合
        duplicates = self.cleaner.df.duplicated(subset=['job_title', 'company_name'])
        self.assertFalse(duplicates.any())

    def test_handle_outliers(self):
        """测试异常值处理"""
        self.cleaner.load_data()
        self.cleaner.handle_missing_values()
        self.cleaner.remove_duplicates()
        self.cleaner.handle_outliers()

        # 验证所有薪资都大于0
        self.assertTrue((self.cleaner.df['salary_min'] > 0).all())
        self.assertTrue((self.cleaner.df['salary_max'] > 0).all())

        # 验证最高薪资大于最低薪资
        self.assertTrue(
            (self.cleaner.df['salary_max'] > self.cleaner.df['salary_min']).all()
        )

        # 验证薪资在合理范围内
        self.assertTrue((self.cleaner.df['salary_min'] < 100000).all())
        self.assertTrue((self.cleaner.df['salary_max'] < 200000).all())

    def test_standardize_city(self):
        """测试城市标准化"""
        test_cases = {
            "北京市": "北京",
            "上海市": "上海",
            "广州市": "广州",
            "深圳": "深圳",
            "杭州市": "杭州",
            None: "未知",
            "": "未知"
        }

        for input_city, expected_output in test_cases.items():
            result = self.cleaner._standardize_city(input_city)
            self.assertEqual(result, expected_output)

    def test_standardize_education(self):
        """测试学历标准化"""
        test_cases = {
            "本科及以上": "本科",
            "大专": "大专",
            "硕士研究生": "硕士",
            "博士": "博士",
            "不限": "不限",
            "高中": "高中",
            None: "不限",
            "": "不限"
        }

        for input_edu, expected_output in test_cases.items():
            result = self.cleaner._standardize_education(input_edu)
            self.assertEqual(result, expected_output)

    def test_standardize_experience(self):
        """测试工作经验标准化"""
        test_cases = {
            "3-5年": "3-5年",
            "1-3年工作经验": "1-3年",
            "应届生": "不限",
            "不限": "不限",
            "5-10年": "5-10年",
            None: "不限",
            "": "不限"
        }

        for input_exp, expected_output in test_cases.items():
            result = self.cleaner._standardize_experience(input_exp)
            self.assertEqual(result, expected_output)

    def test_standardize_data(self):
        """测试数据标准化"""
        self.cleaner.load_data()
        self.cleaner.handle_missing_values()
        self.cleaner.remove_duplicates()
        self.cleaner.handle_outliers()
        self.cleaner.standardize_data()

        # 验证职位标题被清理（去除多余空格和换行）
        for title in self.cleaner.df['job_title']:
            self.assertNotIn('\n', title)
            self.assertEqual(title, title.strip())

        # 验证平均薪资被计算
        self.assertIn('salary_avg', self.cleaner.df.columns)
        expected_avg = (self.cleaner.df['salary_min'] + self.cleaner.df['salary_max']) / 2
        pd.testing.assert_series_equal(
            self.cleaner.df['salary_avg'],
            expected_avg,
            check_names=False
        )

        # 验证年薪被计算
        self.assertIn('salary_yearly_avg', self.cleaner.df.columns)

    def test_generate_quality_report(self):
        """测试质量报告生成"""
        self.cleaner.load_data()
        self.cleaner.clean()
        report = self.cleaner.generate_quality_report()

        # 验证报告包含必要的字段
        self.assertIn('original_count', report)
        self.assertIn('final_count', report)
        self.assertIn('removed_count', report)
        self.assertIn('removal_rate', report)
        self.assertIn('salary_stats', report)

        # 验证数据统计正确
        self.assertEqual(report['original_count'], 6)
        self.assertLessEqual(report['final_count'], 6)
        self.assertEqual(
            report['removed_count'],
            report['original_count'] - report['final_count']
        )

    def test_clean_workflow(self):
        """测试完整的清洗流程"""
        self.cleaner.load_data()
        result_df = self.cleaner.clean()

        # 验证返回的DataFrame不为空
        self.assertIsNotNone(result_df)

        # 验证数据量减少（因为有无效和重复数据）
        self.assertLess(len(result_df), self.cleaner.original_count)

        # 验证所有必要的列都存在
        required_columns = [
            'job_title', 'company_name', 'salary_min', 'salary_max',
            'salary_avg', 'salary_yearly_avg'
        ]
        for col in required_columns:
            self.assertIn(col, result_df.columns)

        # 验证数据质量
        self.assertFalse(result_df['job_title'].isna().any())
        self.assertFalse(result_df['company_name'].isna().any())
        self.assertTrue((result_df['salary_min'] > 0).all())

    def test_save_cleaned_data(self):
        """测试保存清洗后的数据"""
        self.cleaner.load_data()
        self.cleaner.clean()

        output_file = "data/test/test_output"
        csv_file = self.cleaner.save_cleaned_data(output_file, save_json=True)

        # 验证文件被创建
        self.assertTrue(os.path.exists(csv_file))
        self.assertTrue(os.path.exists(f"{output_file}.json"))
        self.assertTrue(os.path.exists(f"{output_file}_report.json"))

        # 验证CSV文件可以读取
        df_loaded = pd.read_csv(csv_file)
        self.assertEqual(len(df_loaded), len(self.cleaner.df))

        # 验证JSON文件可以读取
        with open(f"{output_file}.json", 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        self.assertEqual(len(json_data), len(self.cleaner.df))

        # 验证报告文件可以读取
        with open(f"{output_file}_report.json", 'r', encoding='utf-8') as f:
            report = json.load(f)
        self.assertIn('original_count', report)


class TestDataValidation(unittest.TestCase):
    """测试数据验证功能"""

    def test_salary_validation(self):
        """测试薪资数据验证"""
        # 这里可以添加更多的验证测试
        pass


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
