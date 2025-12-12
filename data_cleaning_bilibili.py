import pandas as pd
import os

# 读取数据
file_name = "video_info_complete.csv"
df = pd.read_csv(file_name, encoding='utf-8')

# 1转为int
# 需要转换为整数的列
num_cols = ['播放量', '点赞数', '投币数', '收藏数', '分享数',
            'UP主粉丝数', '视频评论数', '视频弹幕数']

# 批量转换
for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')


# 2缺失值处理

print("=== 缺失值检测 ===")
# 检测缺失值（包括NaN和"-"）
def check_missing(column):
    nan_count = column.isnull().sum()
    dash_count = (column == '-').sum()
    return nan_count + dash_count

for col in df.columns:
    missing_count = check_missing(df[col])
    if missing_count > 0:
        print(f"{col}: {missing_count} 个缺失值")

print(f"\n视频简介具体缺失: {check_missing(df['视频简介'])} 个")

# 处理缺失值
print("\n=== 处理缺失值 ===")
df['视频简介'] = df['视频简介'].replace('-', '')  # 将"-"替换为空字符串
df['视频简介'] = df['视频简介'].fillna('')       # 将NaN替换为空字符串

print("处理完成！")
print(f"处理后视频简介缺失值: {check_missing(df['视频简介'])} 个")


# 3时间处理
import pandas as pd
from datetime import datetime

# 读取CSV文件
df = pd.read_csv('video_info_complete.csv', encoding='utf-8-sig')

# 将“发布时间”列转换为datetime类型
df['发布时间'] = pd.to_datetime(df['发布时间'], format='%Y/%m/%d %H:%M', errors='coerce')

# 拆分日期和时间
df['发布日期'] = df['发布时间'].dt.date
df['发布时间'] = df['发布时间'].dt.time

# 将日期列转换回datetime以提取星期几
df['发布日期_dt'] = pd.to_datetime(df['发布日期'])

# 添加星期几列（中文）
df['星期几'] = df['发布日期_dt'].dt.day_name()
weekday_map = {
    'Monday': '星期一',
    'Tuesday': '星期二',
    'Wednesday': '星期三',
    'Thursday': '星期四',
    'Friday': '星期五',
    'Saturday': '星期六',
    'Sunday': '星期日'
}
df['星期几'] = df['星期几'].map(weekday_map)

# 删除临时列
df = df.drop(columns=['发布日期_dt'])

# 重排列顺序，将新列放在“发布时间”附近
cols = df.columns.tolist()
pub_index = cols.index('发布时间')  # 找到原“发布时间”索引
cols = cols[:pub_index] + ['发布日期', '发布时间', '星期几'] + cols[pub_index+1:-1]  # 移除原发布时间并插入新列

# 重新整理列顺序
df = df[cols]

# 直接保存到原文件（覆盖）
df.to_csv('video_info_complete.csv', index=False, encoding='utf-8-sig')

print("处理完成！已直接保存到原文件 'video_info_complete.csv'")
print(df.head())


# 4异常值处理


print("开始异常值检测与处理")

# 定义正常值范围
value_ranges = {
    '播放量': (1000, 100000000),      # 播放量在1000到一亿之间
    '点赞数': (0, 7000000),         # 点赞数在0到700万之间
    '投币数': (0, 7000000),          # 投币数在0到700万之间
    '收藏数': (0, 4000000),         # 收藏数在0到400万之间
    '分享数': (0, 7000000)            # 分享数在0到700万之间
}

# 检测和处理异常值
print("=== 异常值检测 ===")
for column, (min_val, max_val) in value_ranges.items():
    # 检测异常值
    too_low = (df[column] < min_val).sum()
    too_high = (df[column] > max_val).sum()
    total_outliers = too_low + too_high
    
    print(f"{column}:")
    print(f"  低于{min_val}: {too_low} 个")
    print(f"  高于{max_val}: {too_high} 个")
    print(f"  总计异常: {total_outliers} 个")
    
    # 处理异常值 - 用中位数替换
    if total_outliers > 0:
        median_value = df[column].median()
        # 创建掩码标识异常值
        outlier_mask = (df[column] < min_val) | (df[column] > max_val)
        # 用中位数替换异常值
        df.loc[outlier_mask, column] = median_value
        print(f"  已用中位数({median_value})替换异常值")

print("\n异常值处理完成")

# 5. 重复值检查（极简版）
import pandas as pd

def quick_duplicate_check(file="video_info_complete.csv"):
    """
    快速重复检查
    """
    print("=== 重复值检查 ===")
    
    try:
        # 读取数据
        df = pd.read_csv(file, encoding='utf-8-sig')
    except:
        df = pd.read_csv(file, encoding='gbk')
    
    # 检查重复
    results = []
    if '视频链接' in df.columns:
        link_dup = df['视频链接'].duplicated().sum()
        results.append(f"链接重复: {link_dup}")
    
    if '视频标题' in df.columns:
        title_dup = df['视频标题'].duplicated().sum()
        results.append(f"标题重复: {title_dup}")
    
    # 输出结果
    for r in results:
        print(f"✓ {r}")
    
    print("检查完成")
    return df

# 使用
# quick_duplicate_check()



# 7. 另存为新文件
output_filename = 'bilibili_food_cleaned_final.csv'
df.to_csv(output_filename, index=False, encoding='utf-8-sig')

print(f"处理完成！已保存为 '{output_filename}'")
print(f"文件保存在: {os.path.abspath(output_filename)}")
print("\n前几行数据预览:")
print(df.head())