"""
职位推荐系统
基于TF-IDF和余弦相似度的职位推荐算法
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba
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


class JobRecommender:
    """职位推荐器"""

    def __init__(self, model_dir='data/models'):
        """
        初始化推荐器

        Args:
            model_dir: 模型保存目录
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.df = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.feature_names = []

        # 停用词
        self.stop_words = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            '你', '会', '着', '没有', '看', '好', '自己', '这'
        ])

    def load_data(self, data_source):
        """
        加载职位数据

        Args:
            data_source: 数据源（文件路径或DataFrame）
        """
        logger.info("正在加载数据...")

        if isinstance(data_source, pd.DataFrame):
            self.df = data_source
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

    def preprocess_text(self, text):
        """
        预处理文本

        Args:
            text: 输入文本

        Returns:
            处理后的文本
        """
        if pd.isna(text) or not text:
            return ""

        text = str(text).lower()

        # 使用jieba分词
        words = jieba.cut(text)

        # 过滤停用词
        words = [w for w in words if w not in self.stop_words and len(w) > 1]

        return ' '.join(words)

    def build_feature_text(self, row):
        """
        构建特征文本（组合多个字段）

        Args:
            row: 数据行

        Returns:
            组合后的特征文本
        """
        features = []

        # 职位标题（权重较高，重复3次）
        if 'job_title' in row and pd.notna(row['job_title']):
            features.extend([str(row['job_title'])] * 3)

        # 职位描述
        if 'job_description' in row and pd.notna(row['job_description']):
            features.append(str(row['job_description']))

        # 技能标签（权重较高，重复2次）
        if 'job_tags' in row and pd.notna(row['job_tags']):
            tags = str(row['job_tags']).replace(',', ' ')
            features.extend([tags] * 2)

        # 行业
        if 'industry' in row and pd.notna(row['industry']):
            features.append(str(row['industry']))

        # 公司类型
        if 'company_type' in row and pd.notna(row['company_type']):
            features.append(str(row['company_type']))

        # 福利待遇
        if 'welfare' in row and pd.notna(row['welfare']):
            features.append(str(row['welfare']))

        return ' '.join(features)

    def train(self, max_features=500):
        """
        训练推荐模型

        Args:
            max_features: TF-IDF最大特征数
        """
        logger.info("\n" + "="*60)
        logger.info("开始训练职位推荐模型")
        logger.info("="*60)

        if self.df is None:
            raise ValueError("请先加载数据")

        # 构建特征文本
        logger.info("正在构建特征文本...")
        self.df['feature_text'] = self.df.apply(self.build_feature_text, axis=1)

        # 预处理文本
        logger.info("正在预处理文本...")
        processed_texts = [self.preprocess_text(text) for text in self.df['feature_text']]

        # 训练TF-IDF模型
        logger.info(f"正在训练TF-IDF模型 (max_features={max_features})...")
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),  # 使用1-gram和2-gram
            min_df=2,  # 至少出现在2个文档中
            max_df=0.8  # 最多出现在80%的文档中
        )

        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_texts)
        self.feature_names = self.tfidf_vectorizer.get_feature_names_out()

        logger.info(f"✓ TF-IDF矩阵形状: {self.tfidf_matrix.shape}")
        logger.info(f"✓ 特征数量: {len(self.feature_names)}")

        # 打印一些重要特征
        feature_importance = np.asarray(self.tfidf_matrix.sum(axis=0)).ravel()
        top_features_idx = feature_importance.argsort()[-20:][::-1]

        logger.info(f"\n最重要的20个特征:")
        for i, idx in enumerate(top_features_idx, 1):
            logger.info(f"  {i:2d}. {self.feature_names[idx]:20s}: {feature_importance[idx]:.2f}")

        logger.info("\n✓ 模型训练完成！")

    def recommend_by_job_id(self, job_id, top_n=10, return_scores=False):
        """
        基于职位ID推荐相似职位

        Args:
            job_id: 职位索引ID（DataFrame的index）
            top_n: 返回的推荐数量
            return_scores: 是否返回相似度分数

        Returns:
            推荐的职位列表
        """
        if self.tfidf_matrix is None:
            raise ValueError("请先训练模型")

        if job_id not in self.df.index:
            raise ValueError(f"职位ID {job_id} 不存在")

        # 计算相似度
        job_vector = self.tfidf_matrix[job_id]
        similarities = cosine_similarity(job_vector, self.tfidf_matrix).flatten()

        # 获取最相似的职位（排除自己）
        similar_indices = similarities.argsort()[::-1][1:top_n+1]

        # 构建推荐结果
        recommendations = []
        for idx in similar_indices:
            job = self.df.iloc[idx].to_dict()
            job['similarity_score'] = float(similarities[idx])
            job['job_id'] = int(idx)
            recommendations.append(job)

        if return_scores:
            return recommendations
        else:
            return [r['job_id'] for r in recommendations]

    def recommend_by_profile(self, user_profile, top_n=10):
        """
        基于用户画像推荐职位

        Args:
            user_profile: 用户画像字典，包含：
                - skills: 技能列表 (list)
                - experience: 工作经验 (str)
                - education: 学历 (str)
                - preferred_city: 偏好城市 (str)
                - preferred_industry: 偏好行业 (str)
            top_n: 返回的推荐数量

        Returns:
            推荐的职位列表
        """
        if self.tfidf_matrix is None:
            raise ValueError("请先训练模型")

        # 构建用户特征文本
        profile_text = []

        if 'skills' in user_profile and user_profile['skills']:
            # 技能权重最高，重复5次
            skills_text = ' '.join(user_profile['skills'])
            profile_text.extend([skills_text] * 5)

        if 'preferred_industry' in user_profile and user_profile['preferred_industry']:
            # 行业重复3次
            profile_text.extend([user_profile['preferred_industry']] * 3)

        if 'experience' in user_profile and user_profile['experience']:
            profile_text.append(user_profile['experience'])

        if 'education' in user_profile and user_profile['education']:
            profile_text.append(user_profile['education'])

        if 'preferred_city' in user_profile and user_profile['preferred_city']:
            profile_text.append(user_profile['preferred_city'])

        profile_text = ' '.join(profile_text)

        # 预处理
        processed_profile = self.preprocess_text(profile_text)

        # 转换为TF-IDF向量
        profile_vector = self.tfidf_vectorizer.transform([processed_profile])

        # 计算相似度
        similarities = cosine_similarity(profile_vector, self.tfidf_matrix).flatten()

        # 应用过滤条件
        mask = np.ones(len(self.df), dtype=bool)

        # 过滤城市
        if 'preferred_city' in user_profile and user_profile['preferred_city']:
            if 'city' in self.df.columns:
                city_mask = self.df['city'] == user_profile['preferred_city']
                mask &= city_mask

        # 过滤经验要求（如果用户有经验，则不推荐要求更高经验的职位）
        if 'experience' in user_profile and user_profile['experience']:
            exp_order = {'不限': 0, '1年以下': 1, '1-3年': 2, '3-5年': 3, '5-10年': 4, '10年以上': 5}
            user_exp_level = exp_order.get(user_profile['experience'], 0)

            if 'experience' in self.df.columns:
                exp_mask = self.df['experience'].apply(
                    lambda x: exp_order.get(x, 0) <= user_exp_level + 1
                )
                mask &= exp_mask

        # 应用过滤
        filtered_similarities = similarities.copy()
        filtered_similarities[~mask] = -1

        # 获取最相似的职位
        similar_indices = filtered_similarities.argsort()[::-1][:top_n]

        # 构建推荐结果
        recommendations = []
        for idx in similar_indices:
            if filtered_similarities[idx] > 0:  # 只返回有效的推荐
                job = self.df.iloc[idx].to_dict()
                job['similarity_score'] = float(similarities[idx])
                job['job_id'] = int(idx)
                recommendations.append(job)

        return recommendations

    def get_recommendation_explanation(self, job_id, recommended_job_id):
        """
        解释推荐原因

        Args:
            job_id: 原职位ID
            recommended_job_id: 推荐的职位ID

        Returns:
            推荐原因说明
        """
        if self.tfidf_matrix is None:
            raise ValueError("请先训练模型")

        # 获取两个职位的TF-IDF向量
        job_vector = self.tfidf_matrix[job_id].toarray().flatten()
        rec_vector = self.tfidf_matrix[recommended_job_id].toarray().flatten()

        # 找出共同的重要特征
        common_features = []
        for i, (v1, v2) in enumerate(zip(job_vector, rec_vector)):
            if v1 > 0 and v2 > 0:
                importance = min(v1, v2)
                common_features.append((self.feature_names[i], importance))

        # 按重要性排序
        common_features.sort(key=lambda x: x[1], reverse=True)

        # 构建解释
        explanation = {
            'common_keywords': [f[0] for f in common_features[:10]],
            'similarity_score': float(cosine_similarity(
                self.tfidf_matrix[job_id],
                self.tfidf_matrix[recommended_job_id]
            )[0][0])
        }

        return explanation

    def save_model(self, filename=None):
        """
        保存模型

        Args:
            filename: 模型文件名
        """
        if filename is None:
            filename = self.model_dir / 'job_recommender.pkl'

        model_data = {
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'feature_names': self.feature_names,
            'df': self.df
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
            filename = self.model_dir / 'job_recommender.pkl'

        with open(filename, 'rb') as f:
            model_data = pickle.load(f)

        self.tfidf_vectorizer = model_data['tfidf_vectorizer']
        self.feature_names = model_data['feature_names']
        self.df = model_data['df']

        # 重新计算TF-IDF矩阵
        processed_texts = [self.preprocess_text(text) for text in self.df['feature_text']]
        self.tfidf_matrix = self.tfidf_vectorizer.transform(processed_texts)

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

    # 创建推荐器
    recommender = JobRecommender()

    # 加载数据
    recommender.load_data(data_file)

    # 训练模型
    recommender.train(max_features=500)

    # 保存模型
    recommender.save_model()

    # 测试推荐
    logger.info("\n" + "="*60)
    logger.info("测试基于职位的推荐")
    logger.info("="*60)

    job_id = 0
    recommendations = recommender.recommend_by_job_id(job_id, top_n=5, return_scores=True)

    logger.info(f"\n为职位 {job_id} 推荐的相似职位:")
    logger.info(f"原职位: {recommender.df.iloc[job_id]['job_title']}")
    logger.info(f"\n推荐结果:")

    for i, rec in enumerate(recommendations, 1):
        logger.info(f"\n{i}. {rec['job_title']}")
        logger.info(f"   公司: {rec['company_name']}")
        logger.info(f"   薪资: {rec['salary_min']}-{rec['salary_max']} 元/月")
        logger.info(f"   相似度: {rec['similarity_score']:.3f}")

    # 测试基于用户画像的推荐
    logger.info("\n" + "="*60)
    logger.info("测试基于用户画像的推荐")
    logger.info("="*60)

    user_profile = {
        'skills': ['Python', 'Django', 'MySQL', 'Redis'],
        'experience': '3-5年',
        'education': '本科',
        'preferred_city': '北京',
        'preferred_industry': '互联网'
    }

    logger.info(f"\n用户画像:")
    logger.info(f"  技能: {', '.join(user_profile['skills'])}")
    logger.info(f"  经验: {user_profile['experience']}")
    logger.info(f"  学历: {user_profile['education']}")
    logger.info(f"  偏好城市: {user_profile['preferred_city']}")

    recommendations = recommender.recommend_by_profile(user_profile, top_n=5)

    logger.info(f"\n推荐职位:")
    for i, rec in enumerate(recommendations, 1):
        logger.info(f"\n{i}. {rec['job_title']}")
        logger.info(f"   公司: {rec['company_name']}")
        logger.info(f"   城市: {rec['city']}")
        logger.info(f"   薪资: {rec['salary_min']}-{rec['salary_max']} 元/月")
        logger.info(f"   相似度: {rec['similarity_score']:.3f}")


if __name__ == '__main__':
    main()
