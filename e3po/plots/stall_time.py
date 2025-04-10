import pandas as pd
import matplotlib.pyplot as plt
from algorithm_map import csv_files,base_dir

rebuffer_durations = {}

for algo_name, file_path in csv_files.items():
    df = pd.read_csv(base_dir + file_path)

    # 计算 clock 间隔，单位为毫秒
    if len(df['clock']) >= 2:
        interval_ms = df['clock'].iloc[1] - df['clock'].iloc[0]
    else:
        interval_ms = 0  # 或者跳过该算法

    # 卡顿帧数
    rebuffer_count = df['is_rebuffer'].sum()

    # 总卡顿时长（单位：秒）
    total_rebuffer_time = (rebuffer_count * interval_ms) / 1000.0
    rebuffer_durations[algo_name] = total_rebuffer_time

# 绘图
plt.figure(figsize=(8, 5))
bars = plt.bar(rebuffer_durations.keys(), rebuffer_durations.values(), color='coral')
plt.ylabel("总卡顿时长（秒）")
plt.title("不同算法的卡顿总时长对比")
plt.grid(axis='y', linestyle='--', alpha=0.6)

# 在柱子上方标出数值
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, f"{yval:.2f}", ha='center', va='bottom')

plt.tight_layout()
plt.show()
