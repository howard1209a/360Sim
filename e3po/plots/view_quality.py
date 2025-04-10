import pandas as pd
import matplotlib.pyplot as plt
import os
from algorithm_map import base_dir, csv_files

avg_bitrate_dict = {}

for algo_name, file_path in csv_files.items():
    file_path = base_dir + file_path
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        avg_bitrate = df['avg_frame_bitrate'].mean()
        avg_bitrate_dict[algo_name] = avg_bitrate
    else:
        print(f"文件不存在: {file_path}")

# 绘图
plt.figure(figsize=(8, 6))
plt.bar(avg_bitrate_dict.keys(), avg_bitrate_dict.values(), color='cornflowerblue')
plt.ylabel("平均画面比特率（单位依据原始数据）")
plt.title("不同算法的平均画面比特率对比")
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
