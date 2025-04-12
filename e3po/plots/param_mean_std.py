import numpy as np
import matplotlib.pyplot as plt

# 把 eta 列表改为字符串形式
mean_std_list = ["(1.2,24)", "(1.2,50)", "(1.6,24)", "(1.6,50)", "(2.0,24)", "(2.0,50)"]

L_list = [16.71 / 60 + 0.8 * 0.283, 13.37 / 60 + 0.8 * 0.34, 11.37 / 60 + 0.8 * 0.381, 14.62 / 60 + 0.8 * 0.446,
          9.81 / 60 + 0.8 * 0.432, 9.81 / 60 + 0.8 * 0.436]

bit2MB = 8388608.0
R_list = [805060400 / bit2MB, 854791784 / bit2MB, 713180375 / bit2MB, 711434336 / bit2MB, 508292895 / bit2MB,
          470899111 / bit2MB]

fig, ax1 = plt.subplots(figsize=(8, 5))

# 左 y 轴
color_k = "#B24475"
ax1.set_xlabel('(a_mean,a_std)')
ax1.set_ylabel('L', color=color_k)
ax1.plot(mean_std_list, L_list, marker='o', color=color_k, label='L', linestyle='-')
ax1.tick_params(axis='y', labelcolor=color_k)

# 右 y 轴
ax2 = ax1.twinx()
color_r = "#864CBC"
ax2.set_ylabel('Download Data (MB)', color=color_r)
ax2.plot(mean_std_list, R_list, marker='s', color=color_r, label='R', linestyle='-')
ax2.tick_params(axis='y', labelcolor=color_r)

# 网格、布局与显示
plt.title('')
fig.tight_layout()
plt.grid(True)
plt.show()
