import numpy as np
import matplotlib.pyplot as plt

eta_list = [0.4, 0.8, 1.2, 1.6, 2.0]
L_list = [14.62 / 60 + 0.4 * 0.247, 9.81 / 60 + 0.8 * 0.592, 12.92 / 60 + 1.2 * 0.299,
          9.81 / 60 + 1.6 * 0.441, 15.2 / 60 + 2.0 * 0.323]
bit2MB = 8388608.0
R_list = [765914384 / bit2MB, 401921095 / bit2MB, 811088975 / bit2MB, 553681879 / bit2MB, 875802359 / bit2MB]

fig, ax1 = plt.subplots(figsize=(8, 5))

# 左 y 轴
color_k = "#B24475"
ax1.set_xlabel('Eta')
ax1.set_ylabel('L', color=color_k)
ax1.plot(eta_list, L_list, marker='o', color=color_k, label='L', linestyle='-')
ax1.tick_params(axis='y', labelcolor=color_k)

# 右 y 轴
ax2 = ax1.twinx()
color_r = "#864CBC"
ax2.set_ylabel('Download Data(MB)', color=color_r)
ax2.plot(eta_list, R_list, marker='s', color=color_r, label='R', linestyle='-')
ax2.tick_params(axis='y', labelcolor=color_r)

# 网格、布局与显示
plt.title('')
fig.tight_layout()
plt.grid(True)
plt.show()
