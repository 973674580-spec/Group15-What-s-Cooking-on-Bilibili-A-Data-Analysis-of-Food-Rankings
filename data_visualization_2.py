# -*- coding: utf-8 -*-
"""
B站美食视频数据可视化分析
包含5个研究问题的图表:
1. 什么时候发最容易火 - 时间热力图
2. 哪些地方美食最受欢迎 - Top地区柱状图
3. 是否存在文化输出 - 气泡散点图
4. 短vs长视频 - 箱线图
5. 哪种封面更强 - 分类柱状图
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 自定义格式化函数，将数字转换为万为单位
def format_wan(x, pos):
    """将数字格式化为万为单位"""
    if x >= 10000:
        return f'{x/10000:.0f}万'
    return f'{x:.0f}'

def format_wan_detail(x, pos):
    """将数字格式化为万为单位（保留小数）"""
    if x >= 10000:
        return f'{x/10000:.1f}万'
    return f'{x:.0f}'

# 读取数据
df = pd.read_csv('video_info_complete.csv')

# 数据预处理
def parse_duration(duration_str):
    """解析视频时长，返回秒数"""
    if pd.isna(duration_str) or duration_str == '-':
        return None
    try:
        parts = str(duration_str).split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        else:
            return int(parts[0])
    except:
        return None

def parse_datetime(dt_str):
    """解析发布时间"""
    try:
        return pd.to_datetime(dt_str)
    except:
        return None

# 解析时长
df['时长_秒'] = df['视频时长'].apply(parse_duration)
df['发布时间_dt'] = df['发布时间'].apply(parse_datetime)
df['发布小时'] = df['发布时间_dt'].dt.hour
df['发布星期'] = df['发布时间_dt'].dt.dayofweek  # 0=周一

# 计算互动指标
df['总互动'] = df['点赞数'] + df['投币数'] + df['收藏数'] + df['分享数']
df['互动率'] = df['总互动'] / df['播放量'] * 100

# ================== 图1: 时间热力图 ==================
def plot_time_heatmap():
    """什么时候发最容易火 - 时间热力图"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 创建星期-小时的透视表，使用平均播放量
    heatmap_data = df.pivot_table(
        values='播放量', 
        index='发布星期', 
        columns='发布小时', 
        aggfunc='mean'
    )
    
    # 重新索引以包含所有小时
    all_hours = list(range(24))
    heatmap_data = heatmap_data.reindex(columns=all_hours, fill_value=0)
    
    # 星期标签
    weekday_labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    heatmap_data.index = [weekday_labels[i] for i in heatmap_data.index]
    
    # 将播放量转换为万单位用于颜色条显示
    heatmap_data_wan = heatmap_data / 10000
    
    # 绘制热力图
    sns.heatmap(heatmap_data_wan, 
                cmap='YlOrRd', 
                annot=False, 
                fmt='.1f',
                linewidths=0.5,
                cbar_kws={'label': '平均播放量（万）'},
                ax=ax)
    
    ax.set_xlabel('发布小时', fontsize=12)
    ax.set_ylabel('发布星期', fontsize=12)
    ax.set_title('什么时候发视频最容易火 - 时间热力图\n(颜色越深代表平均播放量越高)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('1_时间热力图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("图1 时间热力图 已保存")

# ================== 图2: Top地区柱状图 ==================
def plot_region_bar():
    """哪些地方美食最受欢迎 - Top地区柱状图"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 定义地区关键词
    regions = {
        '东北': ['东北', '沈阳', '哈尔滨', '长春', '大连', '齐齐哈尔'],
        '四川': ['四川', '成都', '重庆', '川菜', '火锅'],
        '广东': ['广东', '广州', '深圳', '潮汕', '粤菜', '佛山'],
        '上海': ['上海'],
        '北京': ['北京'],
        '云南': ['云南', '滇'],
        '新疆': ['新疆', '阿克苏'],
        '西安/陕西': ['西安', '陕西'],
        '日本': ['日本', '大阪'],
        '海外其他': ['芬兰', '丹麦', '美国', '西班牙', '俄罗斯', '泰国', '秘鲁', '中东', '卡塔尔'],
        '广西': ['广西', '玉林', '螺蛳粉'],
        '河南': ['河南', '洛阳'],
        '宁夏': ['宁夏', '辣糊糊'],
    }
    
    region_stats = {}
    
    for region, keywords in regions.items():
        mask = df['视频标题'].str.contains('|'.join(keywords), case=False, na=False) | \
               df['标签'].str.contains('|'.join(keywords), case=False, na=False)
        count = mask.sum()
        if count > 0:
            avg_play = df.loc[mask, '播放量'].mean()
            region_stats[region] = {'数量': count, '平均播放量': avg_play}
    
    # 转换为DataFrame并排序
    region_df = pd.DataFrame(region_stats).T
    region_df = region_df.sort_values('平均播放量', ascending=True)
    
    # 绘制水平柱状图
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(region_df)))
    bars = ax.barh(region_df.index, region_df['平均播放量'], color=colors, edgecolor='white', linewidth=0.5)
    
    # 添加数值标签
    for bar, count in zip(bars, region_df['数量']):
        width = bar.get_width()
        ax.text(width + 50000, bar.get_y() + bar.get_height()/2, 
                f'{width/10000:.1f}万 (n={count})', 
                va='center', fontsize=10)
    
    # 设置坐标轴格式为万单位
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(format_wan))
    
    ax.set_xlabel('平均播放量（万）', fontsize=12)
    ax.set_ylabel('地区/菜系', fontsize=12)
    ax.set_title('哪些地方美食最受欢迎 - Top地区柱状图\n(按平均播放量排序，n=视频数量)', fontsize=14, fontweight='bold')
    ax.set_xlim(0, region_df['平均播放量'].max() * 1.3)
    
    plt.tight_layout()
    plt.savefig('2_地区柱状图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("图2 地区柱状图 已保存")

# ================== 图3: 文化输出气泡散点图 ==================
def plot_culture_bubble():
    """是否存在文化输出 - 气泡散点图"""
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # 定义文化输出相关关键词
    culture_keywords = ['文化输出', '老外', '外国人', '海外', '芬兰', '丹麦', '美国', '西班牙', 
                       '俄罗斯', '日本美食', '泰国', '秘鲁', '中东', '外国人吃', '外国人做中餐',
                       '外国人在中国', '中国美食', '在中国']
    
    # 标记文化输出相关视频
    df['文化输出'] = df['视频标题'].str.contains('|'.join(culture_keywords), case=False, na=False) | \
                     df['标签'].str.contains('|'.join(culture_keywords), case=False, na=False)
    
    # 准备绘图数据
    scatter_df = df[['播放量', '总互动', '点赞数', '文化输出', '视频标题']].dropna()
    
    # 按文化输出分组绘制
    for is_culture, group in scatter_df.groupby('文化输出'):
        label = '文化输出类视频' if is_culture else '普通美食视频'
        color = '#FF6B6B' if is_culture else '#4ECDC4'
        alpha = 0.8 if is_culture else 0.4
        size = group['点赞数'] / 1000  # 气泡大小基于点赞数
        
        ax.scatter(group['播放量'], group['总互动'], 
                  s=size, c=color, alpha=alpha, label=label, edgecolors='white', linewidth=0.5)
    
    # 标注特殊点（文化输出且播放量高的）
    culture_top = scatter_df[scatter_df['文化输出']].nlargest(3, '播放量')
    for _, row in culture_top.iterrows():
        title_short = row['视频标题'][:20] + '...' if len(row['视频标题']) > 20 else row['视频标题']
        ax.annotate(title_short, (row['播放量'], row['总互动']), 
                   fontsize=8, alpha=0.8,
                   xytext=(10, 10), textcoords='offset points')
    
    # 设置坐标轴格式为万单位
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(format_wan))
    ax.yaxis.set_major_formatter(FuncFormatter(format_wan))
    
    ax.set_xlabel('播放量（万）', fontsize=12)
    ax.set_ylabel('总互动数（万）\n(点赞+投币+收藏+分享)', fontsize=12)
    ax.set_title('是否存在文化输出 - 气泡散点图\n(气泡大小=点赞数，红色=文化输出类视频)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    
    # 添加统计信息
    culture_avg = scatter_df[scatter_df['文化输出']]['播放量'].mean()
    normal_avg = scatter_df[~scatter_df['文化输出']]['播放量'].mean()
    stats_text = f'文化输出类平均播放: {culture_avg/10000:.1f}万\n普通类平均播放: {normal_avg/10000:.1f}万'
    ax.text(0.95, 0.05, stats_text, transform=ax.transAxes, fontsize=10, 
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('3_文化输出气泡图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("图3 文化输出气泡图 已保存")



# ================== 图4b: 视频时长分布饼图 ==================
def plot_duration_pie():
    """视频时长分布 - 饼图"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 过滤有效时长数据
    valid_df = df[df['时长_秒'].notna()].copy()
    
    # 将视频分为短、中、长
    def categorize_duration(seconds):
        if seconds <= 60:
            return '短视频\n(≤1分钟)'
        elif seconds <= 300:
            return '中等视频\n(1-5分钟)'
        elif seconds <= 600:
            return '较长视频\n(5-10分钟)'
        else:
            return '长视频\n(>10分钟)'
    
    valid_df['时长类别'] = valid_df['时长_秒'].apply(categorize_duration)
    
    # 定义顺序和颜色
    order = ['短视频\n(≤1分钟)', '中等视频\n(1-5分钟)', '较长视频\n(5-10分钟)', '长视频\n(>10分钟)']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    pie_labels = ['短视频(≤1分钟)', '中等视频(1-5分钟)', '较长视频(5-10分钟)', '长视频(>10分钟)']
    pie_counts = [len(valid_df[valid_df['时长类别']==cat]) for cat in order]
    
    # 计算百分比
    total = sum(pie_counts)
    percentages = [count/total*100 for count in pie_counts]
    
    # 绘制饼图
    wedges, texts, autotexts = ax.pie(
        pie_counts, 
        labels=pie_labels,
        colors=colors,
        autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*total)}个)',
        startangle=90,
        explode=(0.02, 0.02, 0.02, 0.02),
        textprops={'fontsize': 11},
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    
    # 美化自动百分比文字
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
    
    ax.set_title('不同时长视频数量占比 - 饼图', fontsize=14, fontweight='bold')
    
    # 添加图例
    ax.legend(wedges, [f'{label}: {count}个 ({pct:.1f}%)' for label, count, pct in zip(pie_labels, pie_counts, percentages)],
              title="时长类别",
              loc="upper left",
              bbox_to_anchor=(1, 0.9),
              fontsize=10)
    
    plt.tight_layout()
    plt.savefig('4b_视频时长饼图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("图4b 视频时长饼图 已保存")

# ================== 图5: 封面类型分类柱状图 ==================
def plot_cover_bar():
    """哪种封面更强 - 分类柱状图（简化版，只展示播放量和互动率）"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # 根据视频标题和标签推断封面类型
    def classify_cover(row):
        title = str(row['视频标题']).lower()
        tags = str(row['标签']).lower()
        combined = title + ' ' + tags
        
        # 人物类
        if any(word in combined for word in ['博主', 'up主', '美女', '帅哥', '小姐姐', '小哥哥', '闺蜜', '老公', '老婆']):
            return '人物出镜'
        # 美食特写
        elif any(word in combined for word in ['美食', '吃货', '干饭', '美味', '好吃', '香', '味']):
            return '美食特写'
        # 探店类
        elif any(word in combined for word in ['探店', '餐厅', '饭店', '路边摊', '夜市', '摆摊']):
            return '探店场景'
        # 教程类
        elif any(word in combined for word in ['教程', '做法', '制作', '厨艺', '烹饪', '炒', '煮', '烤']):
            return '制作教程'
        # 挑战类
        elif any(word in combined for word in ['挑战', '测评', '试吃', '评测']):
            return '挑战测评'
        # Vlog类
        elif any(word in combined for word in ['vlog', '日常', '记录', '生活']):
            return '日常Vlog'
        else:
            return '其他类型'
    
    df['封面类型'] = df.apply(classify_cover, axis=1)
    
    # 统计每种封面类型的数据
    cover_stats = df.groupby('封面类型').agg({
        '播放量': ['mean', 'count'],
        '互动率': 'mean',
        '点赞数': 'mean'
    }).round(0)
    cover_stats.columns = ['平均播放量', '视频数量', '平均互动率', '平均点赞数']
    cover_stats = cover_stats.sort_values('平均播放量', ascending=True)
    
    # 定义颜色
    colors = plt.cm.Set2(np.linspace(0, 1, len(cover_stats)))
    
    # 图5a: 平均播放量柱状图
    bars1 = axes[0].barh(cover_stats.index, cover_stats['平均播放量'], color=colors, edgecolor='white', linewidth=0.5)
    
    # 添加数值标签
    for bar, count in zip(bars1, cover_stats['视频数量']):
        width_val = bar.get_width()
        axes[0].text(width_val + 10000, bar.get_y() + bar.get_height()/2, 
                f'{width_val/10000:.1f}万 (n={int(count)})', 
                va='center', fontsize=9)
    
    # 设置坐标轴格式为万单位
    from matplotlib.ticker import FuncFormatter
    axes[0].xaxis.set_major_formatter(FuncFormatter(format_wan))
    
    axes[0].set_xlabel('平均播放量（万）', fontsize=12)
    axes[0].set_title('各类型视频平均播放量', fontsize=12, fontweight='bold')
    axes[0].set_xlim(0, cover_stats['平均播放量'].max() * 1.3)
    
    # 图5b: 平均互动率柱状图
    bars2 = axes[1].barh(cover_stats.index, cover_stats['平均互动率'], color=colors, edgecolor='white', linewidth=0.5)
    
    # 添加数值标签
    for bar in bars2:
        width_val = bar.get_width()
        axes[1].text(width_val + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{width_val:.1f}%', 
                va='center', fontsize=9)
    
    axes[1].set_xlabel('平均互动率（%）', fontsize=12)
    axes[1].set_title('各类型视频平均互动率', fontsize=12, fontweight='bold')
    axes[1].set_xlim(0, cover_stats['平均互动率'].max() * 1.3)
    
    fig.suptitle('哪种封面/内容类型更强 - 分类对比\n(基于视频内容类型推断，n=视频数量)', fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig('5_封面类型柱状图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("图5 封面类型柱状图 已保存")

# ================== 执行所有绑图 ==================
if __name__ == '__main__':
    print("="*50)
    print("B站美食视频数据可视化分析")
    print("="*50)
    
    print(f"\n📊 数据概览: 共 {len(df)} 条视频记录\n")
    
    # 生成所有图表
    plot_time_heatmap()
    plot_region_bar()
    plot_culture_bubble()
    plot_duration_boxplot()
    plot_duration_pie()
    plot_cover_bar()
    
    print("\n" + "="*50)
    print("🎉 所有图表已生成完成！")
    print("保存位置: 当前目录下的 PNG 文件")
    print("="*50)


