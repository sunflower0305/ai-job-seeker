"""
薪资预测模型
使用随机森林算法预测职位薪资
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
from pathlib import Path
import logging
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SalaryPredictor:
    """薪资预测器"""

    def __init__(self, model_dir='data/models'):
        """
        初始化预测器

        Args:
            model_dir: 模型保存目录
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.df = None
        self.model = None
        self.label_encoders = {}
        self.feature_columns = []
        self.feature_importance = {}

    def load_data(self, data_source):
        """
        加载职位数据

        Args:
            data_source: 数据源（文件路径或DataFrame）
        """
        logger.info("正在加载数据...")

        if isinstance(data_source, pd.DataFrame):
            self.df = data_source.copy()
        else:
            file_path = Path(data_source)
            if file_path.suffix == '.csv':
                self.df = pd.read_csv(file_path)
            elif file_path.suffix == '.json':
                self.df = pd.read_json(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_path.suffix}")

        logger.info(f"✓ 成功加载 {len(self.df)} 条职位数据")
        return self.df

    def prepare_features(self):
        """准备特征工程"""
        logger.info("正在准备特征...")

        if self.df is None:
            raise ValueError("请先加载数据")

        # 选择特征列
        categorical_features = []
        numerical_features = []

        # 类别特征
        if 'city' in self.df.columns:
            categorical_features.append('city')

        if 'education' in self.df.columns:
            categorical_features.append('education')

        if 'experience' in self.df.columns:
            categorical_features.append('experience')

        if 'industry' in self.df.columns:
            categorical_features.append('industry')

        if 'company_size' in self.df.columns:
            categorical_features.append('company_size')

        if 'company_type' in self.df.columns:
            categorical_features.append('company_type')

        # 数值特征
        if 'salary_months' in self.df.columns:
            numerical_features.append('salary_months')

        # 技能数量特征
        if 'job_tags' in self.df.columns:
            self.df['skills_count'] = self.df['job_tags'].apply(
                lambda x: len(str(x).split(',')) if pd.notna(x) and x else 0
            )
            numerical_features.append('skills_count')

        # 技能分类特征（如果存在）
        for cat in ['skills_languages', 'skills_web_frameworks', 'skills_databases',
                    'skills_big_data', 'skills_ml_ai', 'skills_devops', 'skills_mobile']:
            if cat in self.df.columns:
                # 转换为数量
                self.df[f'{cat}_count'] = self.df[cat].apply(
                    lambda x: len(str(x).split(',')) if pd.notna(x) and x else 0
                )
                numerical_features.append(f'{cat}_count')

        logger.info(f"类别特征: {categorical_features}")
        logger.info(f"数值特征: {numerical_features}")

        # 编码类别特征
        for feature in categorical_features:
            if feature not in self.label_encoders:
                self.label_encoders[feature] = LabelEncoder()
                self.df[f'{feature}_encoded'] = self.label_encoders[feature].fit_transform(
                    self.df[feature].astype(str)
                )
            else:
                self.df[f'{feature}_encoded'] = self.label_encoders[feature].transform(
                    self.df[feature].astype(str)
                )

        # 准备最终特征列表
        self.feature_columns = [f'{f}_encoded' for f in categorical_features] + numerical_features

        logger.info(f"✓ 特征准备完成，共 {len(self.feature_columns)} 个特征")

        return self.feature_columns

    def train(self, target='salary_avg', test_size=0.2, random_state=42):
        """
        训练预测模型

        Args:
            target: 目标变量（默认为salary_avg）
            test_size: 测试集比例
            random_state: 随机种子
        """
        logger.info("\n" + "="*60)
        logger.info("开始训练薪资预测模型")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        if not self.feature_columns:
            self.prepare_features()

        # 准备数据
        X = self.df[self.feature_columns]
        y = self.df[target]

        # 分割训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        logger.info(f"训练集大小: {len(X_train)}")
        logger.info(f"测试集大小: {len(X_test)}")

        # 训练随机森林模型
        logger.info("\n正在训练随机森林模型...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        )

        self.model.fit(X_train, y_train)

        # 评估模型
        logger.info("\n模型评估:")

        # 训练集评估
        y_train_pred = self.model.predict(X_train)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        train_r2 = r2_score(y_train, y_train_pred)

        logger.info(f"训练集:")
        logger.info(f"  MAE: {train_mae:.2f} 元")
        logger.info(f"  RMSE: {train_rmse:.2f} 元")
        logger.info(f"  R²: {train_r2:.4f}")

        # 测试集评估
        y_test_pred = self.model.predict(X_test)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_r2 = r2_score(y_test, y_test_pred)

        logger.info(f"测试集:")
        logger.info(f"  MAE: {test_mae:.2f} 元")
        logger.info(f"  RMSE: {test_rmse:.2f} 元")
        logger.info(f"  R²: {test_r2:.4f}")

        # 交叉验证
        logger.info("\n进行5折交叉验证...")
        cv_scores = cross_val_score(
            self.model, X, y, cv=5,
            scoring='neg_mean_absolute_error',
            n_jobs=-1
        )
        cv_mae = -cv_scores.mean()
        logger.info(f"交叉验证 MAE: {cv_mae:.2f} ± {cv_scores.std():.2f} 元")

        # 特征重要性
        self.feature_importance = dict(zip(
            self.feature_columns,
            self.model.feature_importances_
        ))

        # 按重要性排序
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )

        logger.info(f"\n特征重要性 (Top 10):")
        for i, (feature, importance) in enumerate(sorted_features[:10], 1):
            logger.info(f"  {i:2d}. {feature:30s}: {importance:.4f}")

        logger.info("\n✓ 模型训练完成！")

        # 返回评估指标
        metrics = {
            'train': {'mae': train_mae, 'rmse': train_rmse, 'r2': train_r2},
            'test': {'mae': test_mae, 'rmse': test_rmse, 'r2': test_r2},
            'cv_mae': cv_mae,
            'feature_importance': self.feature_importance
        }

        return metrics

    def predict(self, job_features):
        """
        预测单个职位的薪资

        Args:
            job_features: 职位特征字典，包含：
                - city: 城市
                - education: 学历要求
                - experience: 工作经验
                - industry: 行业
                - company_size: 公司规模
                - company_type: 公司类型
                - salary_months: 薪资月数
                - skills: 技能列表（可选）

        Returns:
            预测的平均薪资
        """
        if self.model is None:
            raise ValueError("请先训练模型")

        # 构建特征向量
        feature_vector = {}

        # 编码类别特征
        categorical_features = ['city', 'education', 'experience', 'industry',
                               'company_size', 'company_type']

        for feature in categorical_features:
            if feature in job_features:
                if feature in self.label_encoders:
                    try:
                        encoded_value = self.label_encoders[feature].transform(
                            [str(job_features[feature])]
                        )[0]
                        feature_vector[f'{feature}_encoded'] = encoded_value
                    except ValueError:
                        # 未见过的类别，使用默认值
                        feature_vector[f'{feature}_encoded'] = 0
                else:
                    feature_vector[f'{feature}_encoded'] = 0

        # 数值特征
        if 'salary_months' in job_features:
            feature_vector['salary_months'] = job_features['salary_months']
        else:
            feature_vector['salary_months'] = 12  # 默认值

        # 技能数量
        if 'skills' in job_features and job_features['skills']:
            if isinstance(job_features['skills'], list):
                feature_vector['skills_count'] = len(job_features['skills'])
            else:
                feature_vector['skills_count'] = len(str(job_features['skills']).split(','))
        else:
            feature_vector['skills_count'] = 0

        # 技能分类特征（如果模型有训练）
        for cat in ['skills_languages', 'skills_web_frameworks', 'skills_databases',
                    'skills_big_data', 'skills_ml_ai', 'skills_devops', 'skills_mobile']:
            feature_name = f'{cat}_count'
            if feature_name in self.feature_columns:
                feature_vector[feature_name] = 0  # 默认值

        # 确保所有特征都存在
        for feature in self.feature_columns:
            if feature not in feature_vector:
                feature_vector[feature] = 0

        # 构建DataFrame
        X = pd.DataFrame([feature_vector])[self.feature_columns]

        # 预测
        prediction = self.model.predict(X)[0]

        return float(prediction)

    def predict_with_confidence(self, job_features):
        """
        预测薪资并计算预测置信度

        Args:
            job_features: 职位特征

        Returns:
            dict: {
                'predicted_salary': 预测平均薪资,
                'salary_min': 最低薪资估计 (80% 置信区间),
                'salary_max': 最高薪资估计 (80% 置信区间),
                'confidence': 预测置信度 (0-1)
            }
        """
        if self.model is None:
            raise ValueError("请先训练或加载模型")

        # 准备特征
        X = self._prepare_single_feature(job_features)

        # 使用随机森林的所有树进行预测
        predictions = np.array([tree.predict(X)[0] for tree in self.model.estimators_])

        # 计算平均薪资
        avg_salary = predictions.mean()

        # 计算标准差和变异系数
        std = predictions.std()
        cv = std / avg_salary if avg_salary > 0 else 1  # 变异系数 (Coefficient of Variation)

        # 计算置信度：基于预测的一致性
        # 变异系数越小，置信度越高
        # 针对小数据集调整后的映射 (训练集仅309个样本):
        # cv < 0.20: 高置信度 (>80%)
        # cv = 0.30: 中等置信度 (~60%)
        # cv = 0.40: 一般置信度 (~40%)
        # cv = 0.50: 低置信度 (~25%)
        # cv > 0.60: 极低置信度 (<15%)

        # 使用更宽松的sigmoid函数
        confidence = 1 / (1 + np.exp(10 * (cv - 0.35)))

        # 确保置信度不会太低（最低15%）
        confidence = max(confidence, 0.15)

        # 计算80%置信区间
        from scipy import stats
        z_score = stats.norm.ppf(0.9)  # 80% 置信区间
        margin = z_score * std

        min_salary = max(avg_salary - margin, 0)
        max_salary = avg_salary + margin

        return {
            'predicted_salary': float(avg_salary),
            'salary_min': float(min_salary),
            'salary_max': float(max_salary),
            'confidence': float(confidence),
            'std': float(std),
            'cv': float(cv)
        }

    def predict_salary_range(self, job_features, confidence=0.8):
        """
        预测薪资范围

        Args:
            job_features: 职位特征
            confidence: 置信区间（默认80%）

        Returns:
            (预测平均薪资, 最低薪资估计, 最高薪资估计)
        """
        avg_salary = self.predict(job_features)

        # 使用随机森林的所有树进行预测，计算标准差
        X = self._prepare_single_feature(job_features)
        predictions = np.array([tree.predict(X)[0] for tree in self.model.estimators_])

        std = predictions.std()

        # 计算置信区间
        from scipy import stats
        z_score = stats.norm.ppf((1 + confidence) / 2)

        margin = z_score * std

        min_salary = max(avg_salary - margin, 0)
        max_salary = avg_salary + margin

        return avg_salary, min_salary, max_salary

    def _prepare_single_feature(self, job_features):
        """准备单个样本的特征"""
        feature_vector = {}

        categorical_features = ['city', 'education', 'experience', 'industry',
                               'company_size', 'company_type']

        for feature in categorical_features:
            if feature in job_features and feature in self.label_encoders:
                try:
                    encoded_value = self.label_encoders[feature].transform(
                        [str(job_features[feature])]
                    )[0]
                    feature_vector[f'{feature}_encoded'] = encoded_value
                except ValueError:
                    feature_vector[f'{feature}_encoded'] = 0
            else:
                feature_vector[f'{feature}_encoded'] = 0

        feature_vector['salary_months'] = job_features.get('salary_months', 12)

        if 'skills' in job_features and job_features['skills']:
            if isinstance(job_features['skills'], list):
                feature_vector['skills_count'] = len(job_features['skills'])
            else:
                feature_vector['skills_count'] = len(str(job_features['skills']).split(','))
        else:
            feature_vector['skills_count'] = 0

        for cat in ['skills_languages', 'skills_web_frameworks', 'skills_databases',
                    'skills_big_data', 'skills_ml_ai', 'skills_devops', 'skills_mobile']:
            feature_name = f'{cat}_count'
            if feature_name in self.feature_columns:
                feature_vector[feature_name] = 0

        for feature in self.feature_columns:
            if feature not in feature_vector:
                feature_vector[feature] = 0

        return pd.DataFrame([feature_vector])[self.feature_columns]

    def save_model(self, filename=None):
        """
        保存模型

        Args:
            filename: 模型文件名
        """
        if filename is None:
            filename = self.model_dir / 'salary_predictor.pkl'

        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'feature_importance': self.feature_importance
        }

        with open(filename, 'wb') as f:
            pickle.dump(model_data, f)

        logger.info(f"✓ 模型已保存: {filename}")

    def load_model(self, filename=None):
        """
        加载模型

        Args:
            filename: 模型文件名
        """
        if filename is None:
            filename = self.model_dir / 'salary_predictor.pkl'

        with open(filename, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.label_encoders = model_data['label_encoders']
        self.feature_columns = model_data['feature_columns']
        self.feature_importance = model_data['feature_importance']

        logger.info(f"✓ 模型已加载: {filename}")


def main():
    """主函数 - 示例用法"""
    from pathlib import Path
    import glob

    # 获取项目根目录
    project_root = Path(__file__).parent.parent

    # 查找清洗后的数据
    data_files = glob.glob(str(project_root / 'data/processed/test_cleaned_jobs.csv'))
    if not data_files:
        data_files = glob.glob(str(project_root / 'data/processed/cleaned_jobs_*.csv'))

    if not data_files:
        logger.error("未找到清洗后的数据文件")
        return

    data_file = data_files[0]
    logger.info(f"使用数据文件: {data_file}")

    # 创建预测器
    predictor = SalaryPredictor()

    # 加载数据
    predictor.load_data(data_file)

    # 训练模型
    metrics = predictor.train()

    # 保存模型
    predictor.save_model()

    # 测试预测
    logger.info("\n" + "="*60)
    logger.info("测试薪资预测")
    logger.info("="*60)

    test_jobs = [
        {
            'city': '北京',
            'education': '本科',
            'experience': '3-5年',
            'industry': '互联网',
            'company_size': '100-499人',
            'company_type': '民营',
            'salary_months': 13,
            'skills': ['Python', 'Django', 'MySQL', 'Redis']
        },
        {
            'city': '上海',
            'education': '硕士',
            'experience': '5-10年',
            'industry': '金融',
            'company_size': '1000-9999人',
            'company_type': '上市公司',
            'salary_months': 14,
            'skills': ['Java', 'Spring', 'MySQL', 'Redis', 'Kafka']
        },
        {
            'city': '深圳',
            'education': '大专',
            'experience': '1-3年',
            'industry': '电子商务',
            'company_size': '20-99人',
            'company_type': '创业公司',
            'salary_months': 12,
            'skills': ['Vue', 'JavaScript', 'HTML', 'CSS']
        }
    ]

    for i, job in enumerate(test_jobs, 1):
        logger.info(f"\n测试职位 {i}:")
        logger.info(f"  城市: {job['city']}")
        logger.info(f"  学历: {job['education']}")
        logger.info(f"  经验: {job['experience']}")
        logger.info(f"  行业: {job['industry']}")
        logger.info(f"  技能: {', '.join(job['skills'])}")

        # 预测薪资
        predicted_salary = predictor.predict(job)
        logger.info(f"\n  预测平均薪资: {predicted_salary:.0f} 元/月")

        # 预测薪资范围
        avg, min_sal, max_sal = predictor.predict_salary_range(job)
        logger.info(f"  预测薪资范围: {min_sal:.0f} - {max_sal:.0f} 元/月 (80%置信区间)")
        logger.info(f"  年薪估计: {avg * job['salary_months'] / 10000:.1f} 万元")


if __name__ == '__main__':
    main()
