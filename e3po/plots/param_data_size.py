# import numpy as np
# import matplotlib.pyplot as plt
#
# data_size_list = [2,4,6,8]
# L_list = [ 19.47/ 60 + 0.8 *0.234, 19.47/ 60 + 0.8 *0.234, / 60 + 0.8 *, / 60 + 0.8 *,
# / 60 + 0.8 *, / 60 + 0.8 *]
# bit2MB = 8388608.0
# R_list = [ 804158919/ bit2MB, 804158919/ bit2MB, 804158919/ bit2MB, / bit2MB, / bit2MB]
#
# fig, ax1 = plt.subplots(figsize=(8, 5))
#
# # 左 y 轴
# color_k = "#B24475"
# ax1.set_xlabel('Eta')
# ax1.set_ylabel('L', color=color_k)
# ax1.plot(eta_list, L_list, marker='o', color=color_k, label='L', linestyle='-')
# ax1.tick_params(axis='y', labelcolor=color_k)
#
# # 右 y 轴
# ax2 = ax1.twinx()
# color_r = "#864CBC"
# ax2.set_ylabel('Download Data(MB)', color=color_r)
# ax2.plot(eta_list, R_list, marker='s', color=color_r, label='R', linestyle='-')
# ax2.tick_params(axis='y', labelcolor=color_r)
#
# # 网格、布局与显示
# plt.title('')
# fig.tight_layout()
# plt.grid(True)
# plt.show()
