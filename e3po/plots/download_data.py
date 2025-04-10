import pandas as pd
import matplotlib.pyplot as plt
import os
from algorithm_map import csv_files, base_dir

total_download_data = {}

for algo_name, file_path in csv_files.items():
    file_path = base_dir + file_path
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        total_data = df['download_data_in_interval'].sum()
        total_download_data[algo_name] = total_data
    else:
        print(f"文件不存在: {file_path}")

# 绘制柱状图
plt.figure(figsize=(8, 6))
plt.bar(total_download_data.keys(), total_download_data.values(), color='mediumseagreen')
plt.ylabel("下载总数据量（单位依据原始数据，比如 KB/MB）")
plt.title("不同算法的下载总数据量对比")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
