"""
数据分析模块
包含三个分析方向的数据处理
"""

import pandas as pd
import numpy as np


def load_data(filepath='Teen_Mental_Health_Dataset.csv'):
    """加载数据"""
    df = pd.read_csv(filepath)
    return df


def clean_data(df):
    """数据清洗和预处理"""
    # 删除重复行
    df = df.drop_duplicates()

    # 检查缺失值并填充
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    # 分类变量填充众数
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else 'unknown')

    return df


def descriptive_analysis(df):
    """方向一：描述性统计分析"""
    numeric_cols = ['age', 'daily_social_media_hours', 'sleep_hours',
                    'screen_time_before_sleep', 'academic_performance',
                    'physical_activity', 'stress_level', 'anxiety_level',
                    'addiction_level']

    # 数值变量统计
    stats = df[numeric_cols].describe().round(2)
    stats_dict = stats.to_dict()

    # 分类变量统计
    gender_stats = df['gender'].value_counts().to_dict()
    platform_stats = df['platform_usage'].value_counts().to_dict()
    social_stats = df['social_interaction_level'].value_counts().to_dict()

    # 抑郁症分组对比
    group_stats = df.groupby('depression_label')[numeric_cols].mean().round(2)
    group_stats_dict = group_stats.to_dict()

    return {
        'stats': stats_dict,
        'gender': gender_stats,
        'platform': platform_stats,
        'social': social_stats,
        'group_comparison': group_stats_dict,
        'depression_rate': f"{(df['depression_label'].mean() * 100):.1f}%"
    }


def correlation_analysis(df):
    """方向二：相关性分析"""
    numeric_cols = ['age', 'daily_social_media_hours', 'sleep_hours',
                    'screen_time_before_sleep', 'academic_performance',
                    'physical_activity', 'stress_level', 'anxiety_level',
                    'addiction_level', 'depression_label']

    corr_matrix = df[numeric_cols].corr()

    # 提取与抑郁症的相关性
    corr_with_depression = corr_matrix['depression_label'].drop('depression_label')
    corr_dict = corr_with_depression.sort_values(ascending=False).to_dict()

    return {
        'corr_matrix': corr_matrix.values.tolist(),
        'columns': numeric_cols,
        'corr_with_depression': corr_dict
    }


def factor_analysis(df):
    """方向三：影响因素分析"""
    # 按社交媒体时长分组
    df['social_group'] = pd.cut(df['daily_social_media_hours'],
                                bins=[0, 2, 4, 6, 10],
                                labels=['<2小时', '2-4小时', '4-6小时', '>6小时'])
    social_depression = df.groupby('social_group')['depression_label'].mean().round(3) * 100

    # 按睡眠时长分组
    df['sleep_group'] = pd.cut(df['sleep_hours'],
                               bins=[0, 5, 7, 8, 10],
                               labels=['<5小时', '5-7小时', '7-8小时', '>8小时'])
    sleep_depression = df.groupby('sleep_group')['depression_label'].mean().round(3) * 100

    # 按年龄分组
    df['age_group'] = pd.cut(df['age'], bins=[12, 14, 16, 18, 20],
                             labels=['13-14岁', '15-16岁', '17-18岁', '19岁'])
    age_depression = df.groupby('age_group')['depression_label'].mean().round(3) * 100

    # 按压力水平分组
    df['stress_group'] = pd.cut(df['stress_level'], bins=[0, 3, 6, 8, 11],
                                labels=['低压力(1-3)', '中压力(4-6)', '高压力(7-8)', '极高压力(9-10)'])
    stress_depression = df.groupby('stress_group')['depression_label'].mean().round(3) * 100

    # 按焦虑水平分组
    df['anxiety_group'] = pd.cut(df['anxiety_level'], bins=[0, 3, 6, 8, 11],
                                 labels=['低焦虑(1-3)', '中焦虑(4-6)', '高焦虑(7-8)', '极高焦虑(9-10)'])
    anxiety_depression = df.groupby('anxiety_group')['depression_label'].mean().round(3) * 100

    # 高风险组对比
    high_risk = df[df['depression_label'] == 1]
    low_risk = df[df['depression_label'] == 0]

    risk_comparison = {
        '社交媒体时长': round(
            high_risk['daily_social_media_hours'].mean() - low_risk['daily_social_media_hours'].mean(), 2),
        '睡眠时长': round(high_risk['sleep_hours'].mean() - low_risk['sleep_hours'].mean(), 2),
        '压力水平': round(high_risk['stress_level'].mean() - low_risk['stress_level'].mean(), 2),
        '焦虑水平': round(high_risk['anxiety_level'].mean() - low_risk['anxiety_level'].mean(), 2),
        '成瘾程度': round(high_risk['addiction_level'].mean() - low_risk['addiction_level'].mean(), 2)
    }

    return {
        'social_depression': social_depression.to_dict(),
        'sleep_depression': sleep_depression.to_dict(),
        'age_depression': age_depression.to_dict(),
        'stress_depression': stress_depression.to_dict(),
        'anxiety_depression': anxiety_depression.to_dict(),
        'risk_comparison': risk_comparison
    }