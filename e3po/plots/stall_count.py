import pandas as pd
import matplotlib.pyplot as plt
from algorithm_map import csv_files,base_dir

rebuffer_counts = {}

for algo_name, file_path in csv_files.items():
    df = pd.read_csv(base_dir + file_path)

    # 确保 is_rebuffer 是布尔值
    df['is_rebuffer'] = df['is_rebuffer'].astype(bool)

    # 找出从 False -> True 的状态跳变次数
    rebuffer_transitions = (df['is_rebuffer'].astype(int).diff() == 1).sum() + 1
    rebuffer_counts[algo_name] = rebuffer_transitions

# 绘图
plt.figure(figsize=(8, 5))
bars = plt.bar(rebuffer_counts.keys(), rebuffer_counts.values(), color='skyblue')
plt.ylabel("卡顿次数（从 False 到 True）")
plt.title("不同算法的卡顿次数对比")
plt.grid(axis='y', linestyle='--', alpha=0.6)

# 标注数值
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.3, f"{int(yval)}", ha='center', va='bottom')

plt.tight_layout()
plt.show()
