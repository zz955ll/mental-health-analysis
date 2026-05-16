"""
机器学习预测模块 - 抑郁症风险预测（修复版）
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os


class MentalHealthPredictor:
    """心理健康预测器"""

    def __init__(self, model_path='mental_model.pkl', scaler_path='mental_scaler.pkl'):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self.feature_cols = None

    def train(self, data_path='../Teen_Mental_Health_Dataset.csv'):
        """训练模型"""
        # 尝试多个路径
        if not os.path.exists(data_path):
            data_path = 'Teen_Mental_Health_Dataset.csv'
        if not os.path.exists(data_path):
            data_path = 'D:/PythonProject/PythonProject1/实训项目/Teen_Mental_Health_Dataset.csv'

        print(f"加载数据: {data_path}")
        df = pd.read_csv(data_path)
        print(f"数据形状: {df.shape}")

        # 特征列（只使用数值型特征，避免分类变量问题）
        self.feature_cols = [
            'daily_social_media_hours',
            'sleep_hours',
            'screen_time_before_sleep',
            'academic_performance',
            'physical_activity',
            'stress_level',
            'anxiety_level',
            'addiction_level'
        ]

        X = df[self.feature_cols].copy()
        y = df['depression_label'].copy()

        # 处理缺失值
        X = X.fillna(X.mean())

        print(f"特征数据形状: {X.shape}")
        print(f"标签分布: {y.value_counts().to_dict()}")

        # 标准化
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        # 训练模型
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        self.model.fit(X_train, y_train)

        # 评估
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        # 特征重要性
        importance = dict(zip(self.feature_cols, self.model.feature_importances_))

        # 保存模型
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)

        print(f"训练完成！训练集准确率: {train_score:.4f}, 测试集准确率: {test_score:.4f}")

        return {
            'train_score': round(train_score, 4),
            'test_score': round(test_score, 4),
            'feature_importance': importance,
            'sample_count': len(df),
            'feature_count': len(self.feature_cols)
        }

    def predict(self, data):
        """预测单个样本的抑郁风险"""
        if self.model is None:
            self.load_model()

        # 处理输入数据
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = data.copy()

        # 只使用数值特征
        X = df[self.feature_cols].fillna(0)
        X_scaled = self.scaler.transform(X)

        # 预测
        proba = self.model.predict_proba(X_scaled)[:, 1]
        prediction = self.model.predict(X_scaled)

        return {
            'depression_risk': float(proba[0]),
            'prediction': int(prediction[0]),
            'risk_level': self._get_risk_level(proba[0]),
            'risk_percentage': f"{proba[0] * 100:.1f}%"
        }

    def load_model(self):
        """加载已保存的模型"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            self.feature_cols = [
                'daily_social_media_hours', 'sleep_hours', 'screen_time_before_sleep',
                'academic_performance', 'physical_activity', 'stress_level',
                'anxiety_level', 'addiction_level'
            ]
        else:
            raise FileNotFoundError("模型文件不存在，请先训练模型")

    def _get_risk_level(self, risk):
        """获取风险等级"""
        if risk < 0.05:
            return '低风险'
        elif risk < 0.15:
            return '中风险'
        else:
            return '高风险'


# 全局实例
predictor = MentalHealthPredictor()


def train_model():
    """训练模型"""
    return predictor.train()


def predict_risk(data):
    """预测抑郁风险"""
    return predictor.predict(data)


def get_model_status():
    """获取模型状态"""
    return {
        'is_trained': os.path.exists(predictor.model_path),
        'model_path': predictor.model_path
    }