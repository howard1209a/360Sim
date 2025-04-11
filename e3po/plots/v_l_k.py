import numpy as np
import matplotlib.pyplot as plt

# === 1. 读取数据 ===
# 假设你的 txt 文件是以空格或制表符分隔的
# 第一列：yaw角速度 (rad/s)
# 第二列：pitch角速度 (rad/s)
# 第三列：k（单位：度）
# 第四列：l（单位：秒）

data = np.loadtxt('/Users/howard1209a/Desktop/codes/E3PO/e3po/result/dynamic_chunk/vega_v_kl.txt')

yaw_rad = data[:, 0]
pitch_rad = data[:, 1]
k_deg = data[:, 2]
l_sec = data[:, 3]

# === 2. 弧度转角度 ===
yaw_deg = np.degrees(yaw_rad)

# === 3. 对 yaw 进行排序 ===
sorted_indices = np.argsort(yaw_deg)
yaw_deg_sorted = yaw_deg[sorted_indices]
k_deg_sorted = k_deg[sorted_indices]
l_sec_sorted = l_sec[sorted_indices]

# === 4. 绘图 ===
fig, ax1 = plt.subplots(figsize=(8, 5))

color_k = "#B24475"
# 左 y 轴 - k
ax1.set_xlabel('Angular Velocity(°/s)')
ax1.set_ylabel('k (°)', color=color_k)
ax1.plot(yaw_deg_sorted, k_deg_sorted, marker='o', color=color_k, label='k (Yaw)', linestyle='-')
ax1.tick_params(axis='y', labelcolor=color_k)

color_l = "#864CBC"
# 右 y 轴 - l
ax2 = ax1.twinx()
ax2.set_ylabel('l (s)', color=color_l)
ax2.plot(yaw_deg_sorted, l_sec_sorted, color=color_l, marker='s', label='l (Yaw)', linestyle='-')
ax2.tick_params(axis='y', labelcolor=color_l)

plt.title('')
fig.tight_layout()
plt.grid(True)
plt.show()
