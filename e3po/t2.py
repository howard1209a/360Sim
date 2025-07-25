import numpy as np
import pandas as pd

# 文件路径
angular_speed_file = 'angular_speed_10ms.txt'
input_data_file = r'D:\codes\360Sim\e3po\result\dynamic_chunk_rebuttal\VegasAgent_5g.csv'

# 读取角速度数据
with open(angular_speed_file, 'r') as f:
    angular_speeds = np.array([float(line.strip()) for line in f.readlines()])

# 读取原始记录
df = pd.read_csv(input_data_file)

# 保证长度匹配
min_len = min(len(angular_speeds), len(df))
angular_speeds = angular_speeds[:min_len]
df = df.iloc[:min_len]

# 添加角速度列
df['angular_speed'] = angular_speeds

# 计算阈值
p33 = np.percentile(angular_speeds, 33)
p66 = np.percentile(angular_speeds, 66)

# 格式化阈值用于文件名
p33_str = f"{p33:.2f}"
p66_str = f"{p66:.2f}"

# 分类函数
def classify_speed(speed):
    if speed < p33:
        return 'low'
    elif speed < p66:
        return 'mid'
    else:
        return 'high'

# 添加分类列
df['speed_level'] = df['angular_speed'].apply(classify_speed)

# 合法文件名
low_file = f'low_speed_lt{p33_str}.txt'
mid_file = f'mid_speed_{p33_str}_{p66_str}.txt'
high_file = f'high_speed_gt{p66_str}.txt'

# 分别保存文件（去掉附加列）
df[df['speed_level'] == 'low'].drop(columns=['angular_speed', 'speed_level']).to_csv(low_file, index=False)
df[df['speed_level'] == 'mid'].drop(columns=['angular_speed', 'speed_level']).to_csv(mid_file, index=False)
df[df['speed_level'] == 'high'].drop(columns=['angular_speed', 'speed_level']).to_csv(high_file, index=False)

print(f"已生成:\n{low_file}\n{mid_file}\n{high_file}")
