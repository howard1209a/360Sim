import pandas as pd
import matplotlib.pyplot as plt
import os
from algorithm_map import csv_files, base_dir

average_latencies = {}

for algo_name, file_path in csv_files.items():
    file_path = base_dir + file_path
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # 计算 latency 的平均值
        avg_latency = df['latency'].mean()
        average_latencies[algo_name] = avg_latency
    else:
        print(f"文件不存在: {file_path}")

# 画图
plt.figure(figsize=(8, 6))
plt.bar(average_latencies.keys(), average_latencies.values(), color='skyblue')
plt.ylabel("平均直播延迟 (ms)")
plt.title("不同算法的平均直播延迟对比")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
