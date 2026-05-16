"""
图表绘制模块 - 纯中文版（使用英文列名映射）
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os


def 创建仪表盘(数据, 分析结果):
    """
    创建交互式仪表盘HTML
    包含三个分析方向的可视化图表
    """

    # 英文列名映射（根据实际CSV文件）
    列名映射 = {
        '社交媒体时长': 'daily_social_media_hours',
        '睡眠时长': 'sleep_hours',
        '学业表现': 'academic_performance',
        '压力水平': 'stress_level',
        '焦虑水平': 'anxiety_level',
        '成瘾程度': 'addiction_level',
        '抑郁标签': 'depression_label',
        '睡前屏幕时间': 'screen_time_before_sleep',
        '体育锻炼': 'physical_activity',
        '年龄': 'age'
    }

    # 反向映射用于显示
    显示名称 = {v: k for k, v in 列名映射.items()}

    # ==================== 图表一：数值变量分布箱线图 ====================
    数值列表 = ['daily_social_media_hours', 'sleep_hours', 'stress_level', 'anxiety_level', 'addiction_level']
    中文名称 = ['社交媒体时长', '睡眠时长', '压力水平', '焦虑水平', '成瘾程度']

    箱线图 = go.Figure()
    for 列名, 中文 in zip(数值列表, 中文名称):
        if 列名 in 数据.columns:
            箱线图.add_trace(go.Box(y=数据[列名], name=中文))

    箱线图.update_layout(
        title='【图表一】关键指标数据分布箱线图',
        xaxis_title='监测指标',
        yaxis_title='指标数值',
        height=500,
        template='plotly_white'
    )

    # ==================== 图表二：抑郁组与非抑郁组雷达对比图 ====================
    对比指标 = ['社交媒体时长', '睡眠时长', '学业表现', '压力水平', '焦虑程度', '成瘾倾向']

    指标对应 = {
        '社交媒体时长': 'daily_social_media_hours',
        '睡眠时长': 'sleep_hours',
        '学业表现': 'academic_performance',
        '压力水平': 'stress_level',
        '焦虑程度': 'anxiety_level',
        '成瘾倾向': 'addiction_level'
    }

    抑郁组数据 = 数据[数据['depression_label'] == 1][list(指标对应.values())].mean().values
    正常组数据 = 数据[数据['depression_label'] == 0][list(指标对应.values())].mean().values

    雷达图 = go.Figure()
    雷达图.add_trace(go.Scatterpolar(
        r=抑郁组数据,
        theta=对比指标,
        fill='toself',
        name='有抑郁倾向组'
    ))
    雷达图.add_trace(go.Scatterpolar(
        r=正常组数据,
        theta=对比指标,
        fill='toself',
        name='无抑郁倾向组'
    ))
    雷达图.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        title='【图表二】抑郁组与非抑郁组指标对比雷达图',
        height=500,
        template='plotly_white'
    )

    # ==================== 图表三：相关性热力图 ====================
    热力变量 = ['daily_social_media_hours', 'sleep_hours', 'screen_time_before_sleep',
               'academic_performance', 'physical_activity', 'stress_level',
               'anxiety_level', 'addiction_level', 'depression_label']

    有效变量 = [变量 for 变量 in 热力变量 if 变量 in 数据.columns]
    相关矩阵 = 数据[有效变量].corr().values
    变量名称 = [显示名称.get(v, v) for v in 有效变量]

    热力图 = go.Figure(data=go.Heatmap(
        z=相关矩阵,
        x=变量名称,
        y=变量名称,
        colorscale='RdBu',
        zmid=0,
        text=np.round(相关矩阵, 2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    热力图.update_layout(
        title='【图表三】心理健康指标相关性热力图',
        height=600,
        width=750,
        template='plotly_white'
    )

    # ==================== 图表四：与抑郁相关性的排序条形图 ====================
    抑郁相关性 = 数据[有效变量].corr()['depression_label'].drop('depression_label')
    相关数据框 = pd.DataFrame({
        '指标名称': [显示名称.get(idx, idx) for idx in 抑郁相关性.index],
        '相关系数': 抑郁相关性.values
    }).sort_values('相关系数', ascending=False)

    颜色列表 = ['#d62728' if x < 0 else '#2ca02c' for x in 相关数据框['相关系数']]

    条形图 = go.Figure(data=go.Bar(
        x=相关数据框['相关系数'],
        y=相关数据框['指标名称'],
        orientation='h',
        marker_color=颜色列表,
        text=相关数据框['相关系数'].round(3),
        textposition='outside'
    ))
    条形图.update_layout(
        title='【图表四】各指标与抑郁症的相关程度排序',
        xaxis_title='相关系数（正值正相关，负值负相关）',
        yaxis_title='影响指标',
        height=500,
        template='plotly_white'
    )

    # ==================== 图表五：社交媒体使用时长与抑郁率 ====================
    数据['社交分组'] = pd.cut(数据['daily_social_media_hours'],
                              bins=[0, 2, 4, 6, 10],
                              labels=['少于2小时', '2至4小时', '4至6小时', '超过6小时'])
    社交抑郁率 = 数据.groupby('社交分组', observed=False)['depression_label'].mean().round(3) * 100

    图表五 = go.Figure(data=go.Bar(
        x=[str(分组) for 分组 in 社交抑郁率.index],
        y=社交抑郁率.values,
        marker_color='#ff7f0e',
        text=[f'{数值:.1f}%' for 数值 in 社交抑郁率.values],
        textposition='outside'
    ))
    图表五.update_layout(
        title='【图表五】每日社交媒体使用时长与抑郁发生率的关系',
        xaxis_title='每日使用社交媒体时长',
        yaxis_title='抑郁发生率（百分比）',
        height=450,
        template='plotly_white'
    )

    # ==================== 图表六：睡眠时长与抑郁率 ====================
    数据['睡眠分组'] = pd.cut(数据['sleep_hours'],
                            bins=[0, 5, 7, 8, 10],
                            labels=['少于5小时', '5至7小时', '7至8小时', '超过8小时'])
    睡眠抑郁率 = 数据.groupby('睡眠分组', observed=False)['depression_label'].mean().round(3) * 100

    图表六 = go.Figure(data=go.Bar(
        x=[str(分组) for 分组 in 睡眠抑郁率.index],
        y=睡眠抑郁率.values,
        marker_color='#1f77b4',
        text=[f'{数值:.1f}%' for 数值 in 睡眠抑郁率.values],
        textposition='outside'
    ))
    图表六.update_layout(
        title='【图表六】每日睡眠时长与抑郁发生率的关系',
        xaxis_title='每日睡眠时长',
        yaxis_title='抑郁发生率（百分比）',
        height=450,
        template='plotly_white'
    )

    # ==================== 图表七：压力水平与抑郁率 ====================
    数据['压力分组'] = pd.cut(数据['stress_level'], bins=[0, 3, 6, 8, 11],
                              labels=['低压力(1-3分)', '中等压力(4-6分)', '高压力(7-8分)', '极高压力(9-10分)'])
    压力抑郁率 = 数据.groupby('压力分组', observed=False)['depression_label'].mean().round(3) * 100

    图表七 = go.Figure(data=go.Bar(
        x=[str(分组) for 分组 in 压力抑郁率.index],
        y=压力抑郁率.values,
        marker_color='#d62728',
        text=[f'{数值:.1f}%' for 数值 in 压力抑郁率.values],
        textposition='outside'
    ))
    图表七.update_layout(
        title='【图表七】压力水平与抑郁发生率的关系',
        xaxis_title='自我评估压力等级',
        yaxis_title='抑郁发生率（百分比）',
        height=450,
        template='plotly_white'
    )

    # ==================== 图表八：焦虑水平与抑郁率 ====================
    数据['焦虑分组'] = pd.cut(数据['anxiety_level'], bins=[0, 3, 6, 8, 11],
                               labels=['低焦虑(1-3分)', '中等焦虑(4-6分)', '高焦虑(7-8分)', '极高焦虑(9-10分)'])
    焦虑抑郁率 = 数据.groupby('焦虑分组', observed=False)['depression_label'].mean().round(3) * 100

    图表八 = go.Figure(data=go.Bar(
        x=[str(分组) for 分组 in 焦虑抑郁率.index],
        y=焦虑抑郁率.values,
        marker_color='#9467bd',
        text=[f'{数值:.1f}%' for 数值 in 焦虑抑郁率.values],
        textposition='outside'
    ))
    图表八.update_layout(
        title='【图表八】焦虑水平与抑郁发生率的关系',
        xaxis_title='自我评估焦虑等级',
        yaxis_title='抑郁发生率（百分比）',
        height=450,
        template='plotly_white'
    )

    return {
        '箱线图': 箱线图,
        '雷达图': 雷达图,
        '热力图': 热力图,
        '条形图': 条形图,
        '社交与抑郁': 图表五,
        '睡眠与抑郁': 图表六,
        '压力与抑郁': 图表七,
        '焦虑与抑郁': 图表八
    }


def 保存所有图表(图表字典, 输出目录='static'):
    """保存所有图表为HTML文件"""
    if not os.path.exists(输出目录):
        os.makedirs(输出目录)

    文件名映射 = {
        '箱线图': '01_数据分布箱线图.html',
        '雷达图': '02_抑郁组对比雷达图.html',
        '热力图': '03_相关性热力图.html',
        '条形图': '04_相关性排序图.html',
        '社交与抑郁': '05_社交媒体与抑郁率.html',
        '睡眠与抑郁': '06_睡眠时长与抑郁率.html',
        '压力与抑郁': '07_压力水平与抑郁率.html',
        '焦虑与抑郁': '08_焦虑水平与抑郁率.html'
    }

    已保存文件 = []
    for 键, 图表 in 图表字典.items():
        if 键 in 文件名映射:
            文件路径 = os.path.join(输出目录, 文件名映射[键])
            图表.write_html(文件路径)
            已保存文件.append(文件路径)
            print(f"  ✓ 已保存: {文件名映射[键]}")

    # 创建汇总仪表盘
    创建汇总仪表盘(输出目录)

    return 已保存文件


def 创建汇总仪表盘(输出目录='static'):
    """创建汇总仪表盘首页"""

    html内容 = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>青少年心理健康数据分析报告</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Microsoft YaHei', 'SimHei', 'PingFang SC', sans-serif; 
            background: #f0f2f5; 
            padding: 20px; 
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .标题 { text-align: center; margin-bottom: 30px; }
        .主标题 { font-size: 32px; color: #1a1a2e; margin-bottom: 10px; font-weight: bold; }
        .副标题 { font-size: 16px; color: #666; }
        .图表网格 { display: grid; grid-template-columns: repeat(auto-fit, minmax(580px, 1fr)); gap: 25px; }
        .图表卡片 { background: white; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; transition: transform 0.3s; }
        .图表卡片:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
        .图表标题 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 20px; font-size: 18px; font-weight: bold; }
        .图表内容 { padding: 15px; background: #fafafa; }
        iframe { width: 100%; height: 480px; border: none; background: white; border-radius: 8px; }
        .页脚 { text-align: center; margin-top: 40px; padding: 20px; color: #888; border-top: 1px solid #ddd; font-size: 14px; }
        @media (max-width: 768px) { .图表网格 { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="标题">
            <div class="主标题">📊 青少年心理健康数据分析报告</div>
            <div class="副标题">基于社交媒体使用、睡眠质量、压力焦虑与抑郁关系的多维度分析</div>
        </div>
        <div class="图表网格">
'''

    图表标题映射 = {
        '01_数据分布箱线图.html': '📊 数据分布箱线图',
        '02_抑郁组对比雷达图.html': '🎯 抑郁组与非抑郁组指标对比',
        '03_相关性热力图.html': '🔥 各指标相关性热力图',
        '04_相关性排序图.html': '📉 与抑郁相关程度排序',
        '05_社交媒体与抑郁率.html': '📱 社交媒体使用与抑郁关系',
        '06_睡眠时长与抑郁率.html': '😴 睡眠时长与抑郁关系',
        '07_压力水平与抑郁率.html': '⚠️ 压力水平与抑郁关系',
        '08_焦虑水平与抑郁率.html': '😰 焦虑水平与抑郁关系'
    }

    for 文件名, 标题 in 图表标题映射.items():
        文件路径 = os.path.join(输出目录, 文件名)
        if os.path.exists(文件路径):
            html内容 += f'''
            <div class="图表卡片">
                <div class="图表标题">{标题}</div>
                <div class="图表内容">
                    <iframe src="{文件名}"></iframe>
                </div>
            </div>
'''

    html内容 += f'''
        </div>
        <div class="页脚">
            <p>📌 数据来源：青少年心理健康调查数据集 | 分析工具：Python + Plotly</p>
            <p>💡 解读说明：相关系数绝对值越接近1表示相关性越强 | 红色代表正相关，蓝色代表负相关</p>
            <p>📅 报告生成时间：{pd.Timestamp.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
'''

    仪表盘路径 = os.path.join(输出目录, '报告首页.html')
    with open(仪表盘路径, 'w', encoding='utf-8') as f:
        f.write(html内容)
    print(f"  ✓ 已保存汇总仪表盘: {仪表盘路径}")

    return 仪表盘路径