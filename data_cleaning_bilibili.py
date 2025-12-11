import pandas as pd

# 读取数据
file_path = r"C:\Users\21666\Desktop\bilibili_food 1207\bilibilifood1.csv"
df = pd.read_csv(file_path, encoding='utf-8')

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
from datetime import datetime

# 处理发布时间
print("2. 处理发布时间...")
# 将发布时间转换为datetime格式
df['发布时间'] = pd.to_datetime(df['发布时间'])

# 拆分为日期列和时间列
df['发布日期'] = df['发布时间'].dt.date
df['发布时间'] = df['发布时间'].dt.time

# 添加星期几列（根据2025年日历）
def get_weekday_chinese(date):
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    return weekdays[date.weekday()]

# 重新读取日期来计算星期几（因为上面已经拆分）
temp_dates = pd.to_datetime(df['发布日期'])
df['星期几'] = temp_dates.apply(get_weekday_chinese)

print("   发布时间处理完成")

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

# 5重复值检测
import pandas as pd

def check_duplicates_simple():
    """
    简洁检查：只检查视频链接和视频标题的重复
    """
    # 文件路径
    file_path = r"C:\Users\21666\Desktop\bilibili_food 1207\bilibili_food_cleaned3.csv"
    
    print("=" * 60)
    print("B站视频数据重复检查（简化版）")
    print("=" * 60)
    
    # 读取数据
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except:
        df = pd.read_csv(file_path, encoding='gbk')
    
    print(f"数据总量: {len(df)} 条记录")
    print("-" * 60)
    
    # 1. 检查视频链接重复
    print("\n1. 视频链接检查")
    print("-" * 40)
    
    if '视频链接' in df.columns:
        link_duplicates = df['视频链接'].duplicated().sum()
        print(f"重复的视频链接: {link_duplicates} 个")
        
        if link_duplicates > 0:
            print("⚠ 发现重复链接！具体重复的链接：")
            dup_links = df[df['视频链接'].duplicated(keep=False)]['视频链接'].unique()
            for link in dup_links[:5]:  # 只显示前5个
                print(f"  - {link}")
                # 显示这个链接对应的所有行
                dup_rows = df[df['视频链接'] == link]
                for idx, row in dup_rows.iterrows():
                    print(f"    行{idx+1}: {row['视频标题'][:40]}... - {row['博主名称']}")
            if len(dup_links) > 5:
                print(f"  ... 还有 {len(dup_links)-5} 个重复链接未显示")
    else:
        print("❌ 数据中没有'视频链接'列")
    
    # 2. 检查视频标题重复
    print("\n2. 视频标题检查")
    print("-" * 40)
    
    if '视频标题' in df.columns:
        title_duplicates = df['视频标题'].duplicated().sum()
        print(f"重复的视频标题: {title_duplicates} 个")
        
        if title_duplicates > 0:
            print("重复的标题：")
            dup_titles = df[df['视频标题'].duplicated(keep=False)]['视频标题'].unique()
            for title in dup_titles[:5]:  # 只显示前5个
                print(f"  - {title[:50]}...")
                # 显示这个标题对应的所有行
                dup_rows = df[df['视频标题'] == title]
                for idx, row in dup_rows.iterrows():
                    print(f"    行{idx+1}: {row['博主名称']} - 链接: {row['视频链接'][-20:]}")
            if len(dup_titles) > 5:
                print(f"  ... 还有 {len(dup_titles)-5} 个重复标题未显示")
    else:
        print("❌ 数据中没有'视频标题'列")
    
    # 3. 生成简洁报告
    print("\n" + "=" * 60)
    print("检查结果汇总")
    print("=" * 60)
    
    results = []
    if '视频链接' in df.columns:
        link_dup_count = df['视频链接'].duplicated().sum()
        results.append(f"视频链接重复: {link_dup_count} 个")
        
    if '视频标题' in df.columns:
        title_dup_count = df['视频标题'].duplicated().sum()
        results.append(f"视频标题重复: {title_dup_count} 个")
    
    for result in results:
        print(f"✓ {result}")
    
    # 4. 保存检查结果
    if '视频链接' in df.columns or '视频标题' in df.columns:
        # 添加重复标记列
        if '视频链接' in df.columns:
            df['链接是否重复'] = df['视频链接'].duplicated(keep=False)
        
        if '视频标题' in df.columns:
            df['标题是否重复'] = df['视频标题'].duplicated(keep=False)
        
        # 保存结果
        output_path = r"C:\Users\21666\Desktop\bilibili_food 1207\bilibilifood1.csv"
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n✓ 检查结果已保存: {output_path}")
        
        # 显示重复数据的行号
        if '链接是否重复' in df.columns:
            dup_link_rows = df[df['链接是否重复']].index.tolist()
            if dup_link_rows:
                print(f"链接重复的行号: {dup_link_rows}")
        
        if '标题是否重复' in df.columns:
            dup_title_rows = df[df['标题是否重复']].index.tolist()
            if dup_title_rows:
                print(f"标题重复的行号（前10个）: {dup_title_rows[:10]}")
                if len(dup_title_rows) > 10:
                    print(f"  ... 总共 {len(dup_title_rows)} 行标题重复")
    
    print("\n检查完成！")
    return df

# 运行检查
if __name__ == "__main__":
    check_duplicates_simple()

# 6去除不必要符号
print("开始清理文本符号...")

# 清理视频标题、标签、类别中的 [ ' ] 符号
def 清理符号(文本):
    if pd.isna(文本) or 文本 == '':
        return ''
    
    文本 = str(文本)
    # 删除 [ ' ] 这些符号
    文本 = 文本.replace('[', '').replace(']', '').replace("'", "")
    return 文本

# 应用清理
df['视频标题'] = df['视频标题'].apply(清理符号)
df['标签'] = df['标签'].apply(清理符号)
df['类别'] = df['类别'].apply(清理符号)

print("符号清理完成！")



# 7. 另存为新文件
output_path = r"C:\Users\21666\Desktop\bilibili_food 1207\bilibili_food_cleaned_final.csv"
df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n清洗后的数据已保存到: {output_path}")