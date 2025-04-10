import pandas as pd
import matplotlib.pyplot as plt
import os
from algorithm_map import csv_files, base_dir

avg_black_ratios = {}

for algo_name, file_path in csv_files.items():
    file_path = base_dir + file_path
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        avg_black = df['black_ratio_in_view'].mean()
        avg_black_ratios[algo_name] = avg_black
    else:
        print(f"文件不存在：{file_path}")

# 画图
plt.figure(figsize=(8, 5))
plt.bar(avg_black_ratios.keys(), avg_black_ratios.values(), color='skyblue')
plt.ylabel('平均黑边比例')
plt.title('不同算法的平均黑边比例对比')

# 动态设置y轴范围
max_value = max(avg_black_ratios.values())
plt.ylim(0, max_value * 1.2)

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
