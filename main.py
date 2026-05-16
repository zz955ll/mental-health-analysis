"""
主程序 - 视图函数
调用分析模块和图表模块，生成HTML报告
"""

import os
import sys

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入分析模块
from analysis import load_data, clean_data, descriptive_analysis, correlation_analysis, factor_analysis

# 导入图表模块（使用中文版函数）
from charts import 创建仪表盘, 保存所有图表


def main():
    """主函数：执行完整分析流程"""
    print("=" * 70)
    print("青少年心理健康数据分析系统")
    print("=" * 70)

    # 1. 获取数据
    print("\n【步骤1】加载数据...")
    df = load_data('Teen_Mental_Health_Dataset.csv')
    print(f"  ✓ 数据加载成功: {df.shape[0]}行, {df.shape[1]}列")

    # 2. 数据处理
    print("\n【步骤2】数据清洗与处理...")
    df = clean_data(df)
    print(f"  ✓ 数据清洗完成")

    # 3. 三个方向的数据分析
    print("\n【步骤3】执行数据分析...")

    # 方向一：描述性分析
    desc_result = descriptive_analysis(df)
    print(f"  ✓ 方向一：描述性分析完成")
    print(f"    - 抑郁检出率: {desc_result['depression_rate']}")

    # 方向二：相关性分析
    corr_result = correlation_analysis(df)
    print(f"  ✓ 方向二：相关性分析完成")
    most_corr = max(corr_result['corr_with_depression'].items(), key=lambda x: abs(x[1]))
    print(f"    - 与抑郁相关性最强的指标: {most_corr[0]} (相关系数: {most_corr[1]:.3f})")

    # 方向三：影响因素分析
    factor_result = factor_analysis(df)
    print(f"  ✓ 方向三：影响因素分析完成")

    # 4. 整合分析结果（用于图表展示）
    analysis_results = {
        'descriptive': desc_result,
        'correlation': corr_result,
        'factor': factor_result,
        'group_comparison': desc_result['group_comparison']
    }

    # 5. 生成图表（使用中文版函数）
    print("\n【步骤4】生成可视化图表...")
    图表字典 = 创建仪表盘(df, analysis_results)

    # 6. 保存HTML文件
    print("\n【步骤5】保存HTML文件...")
    保存所有图表(图表字典, 输出目录='static')

    print("\n" + "=" * 70)
    print("分析完成！")
    print("=" * 70)
    print(f"\n📁 输出文件保存在: {os.path.abspath('static')}")
    print(f"🌐 打开仪表盘: {os.path.abspath('static/报告首页.html')}")

    return analysis_results


def 生成报告():
    """生成报告（供外部调用）"""
    results = main()
    return results


if __name__ == "__main__":
    main()