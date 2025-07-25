import matplotlib.pyplot as plt

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


def format_draw_cdf(list1, list2, list3, list4, list5, list6, x_label):
    num_bins = 15
    max_vx = max(
        max(list1),
        max(list2),
        max(list3),
        max(list4),
        max(list5),
        max(list6),
    )

    # 统一 bin
    bins_vx = np.linspace(0, max_vx, num_bins + 1)

    # === 计算CDF ===
    def compute_cdf(data, bins):
        hist, _ = np.histogram(data, bins=bins)
        percent = hist / hist.sum()
        cdf = np.cumsum(percent)
        return cdf

    cdf_1 = compute_cdf(list1, bins_vx)
    cdf_2 = compute_cdf(list2, bins_vx)
    cdf_3 = compute_cdf(list3, bins_vx)
    cdf_4 = compute_cdf(list4, bins_vx)
    cdf_5 = compute_cdf(list5, bins_vx)
    cdf_6 = compute_cdf(list6, bins_vx)

    # === 绘图 ===
    plt.figure(figsize=(10, 6), dpi=300)
    plt.plot(bins_vx[:-1], cdf_1, marker='o', label='Vaser', color='#B24475')
    plt.plot(bins_vx[:-1], cdf_2, marker='s', label='VAAC', color='#864CBC')
    plt.plot(bins_vx[:-1], cdf_3, marker='^', label='VAAC-E', color='#386688')
    plt.plot(bins_vx[:-1], cdf_4, marker='x', label='PW', color='#845D1C')
    plt.plot(bins_vx[:-1], cdf_5, marker='^', label='BCD', color='#8A543C')
    plt.plot(bins_vx[:-1], cdf_6, marker='x', label='Vega', color='#3D7747')

    plt.xlabel(x_label, fontsize=14)
    plt.ylabel('CDF', fontsize=14)
    plt.grid(True)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()


def format_draw_box(data, my_pal, y_label, pic_name):
    # 设置字体和大小
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams.update({'font.size': 16})

    # 计算最短长度
    min_len = min(len(v) for v in data.values())

    # 截断每个列表
    data = {k: v[:min_len] for k, v in data.items()}

    # 转换为长格式 DataFrame
    df = pd.DataFrame(data).melt(var_name='Solution', value_name='Energy Consumtion(Wh)')

    # 绘图
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Solution', y='Energy Consumtion(Wh)', notch=True, width=0.3, palette=my_pal, data=df)
    sns.swarmplot(x='Solution', y='Energy Consumtion(Wh)', data=df, color="#1E4C9C")

    plt.xlabel('')
    plt.ylabel(y_label)
    plt.show()


# labels是字符串列表，对应每个横轴点
# data是二维列表，长度和labels一致，和labels同一位置即为该横轴点所有柱子的高度
def format_draw_histogram(labels, data, x_label_name, y_label_name, y_bottom):
    plt.rcParams['font.family'] = ['Arial']
    plt.rcParams.update({'font.size': 16})
    # plt.xticks(fontsize=18)
    # plt.yticks(fontsize=18)

    fig, ax = plt.subplots(1, 1, figsize=(8, 4.944))

    ax.set_xlabel(x_label_name, fontsize=16)
    ax.set_ylabel(..., fontsize=16)

    x = np.arange(len(labels))
    width = 0.15

    ax.tick_params(which='major', direction='in', length=5, width=1.5, labelsize=18, bottom=False)
    ax.tick_params(axis='x', labelsize=18, bottom=False, labelrotation=0)

    ax.set_xticks(x)

    ax.set_ylabel(y_label_name)  # Energy Consumption(Wh) Bitrate(Mbps) Delay(s)

    max_value = max(max(row) for row in data)
    ax.set_ylim(bottom=y_bottom, top=max_value * 1.1)

    ax.set_xticklabels(labels)

    linewidth = 1.5
    for spine in ['top', 'bottom', 'left', 'right']:
        ax.spines[spine].set_linewidth(linewidth)

    bar_spacing = 1.1  # 柱子之间的间距倍数（1.0 为紧挨着，越大越松散）

    # 偏移值计算方式（中心对称）
    offsets = [-1.5, -0.5, 0.5, 1.5, 2.5, 3.5]
    offsets = [i * bar_spacing * width for i in offsets]

    # 绘制柱子
    ax.bar(x + offsets[0], [row[0] for row in data], width, label='5g',
           edgecolor='lightgoldenrodyellow', color='#B24475', linewidth=.8, hatch='x')

    ax.bar(x + offsets[1], [row[1] for row in data], width, label='wifi',
           edgecolor='#FAEBD7', color='#864CBC', linewidth=.8, hatch='o')

    ax.bar(x + offsets[2], [row[2] for row in data], width, label='VAAC-E',
           edgecolor='#FAEBD7', color='#386688', linewidth=.8, hatch='/')

    # ax.bar(x + offsets[3], [row[3] for row in data], width, label='PW',
    #        edgecolor='#FAEBD7', color='#845D1C', linewidth=.8, hatch='+')
    #
    # ax.bar(x + offsets[4], [row[4] for row in data], width, label='BCD',
    #        edgecolor='#FAEBD7', color='#8A543C', linewidth=.8, hatch='\\')
    #
    # ax.bar(x + offsets[5], [row[5] for row in data], width, label='Vega',
    #        edgecolor='#FAEBD7', color='#3D7747', linewidth=.8, hatch='//')

    algorithms = ['Vaser', 'VAAC', 'VAAC-E', 'PW', 'BCD', 'Vega']

    # for i in range(len(x)):  # 遍历每个x位置（也就是每组柱子）
    #     for j in range(6):  # 每组里的6个柱子
    #         ax.text(
    #             x[i] + offsets[j],
    #             y_bottom - (max_value * 0.05),  # 让文字在柱子下方一点点
    #             algorithms[j],
    #             ha='center',
    #             va='top',
    #             fontsize=16,
    #             rotation=0
    #         )

    # 保存图像
    plt.savefig('./info.png', dpi=300, bbox_inches='tight')

    plt.show()
# def format_draw_histogram(labels, data, x_label_name, y_label_name, y_bottom):
#     plt.rcParams['font.family'] = ['Arial']
#     plt.xticks(fontsize=18)
#     plt.yticks(fontsize=18)
#
#     fig, ax = plt.subplots(1, 1, figsize=(12, 4))
#
#     ax.set_xlabel(x_label_name, fontsize=20)
#     ax.set_ylabel(..., fontsize=20)
#
#     x = np.arange(len(labels))
#     width = 0.2
#
#     ax.tick_params(which='major', direction='in', length=5, width=1.5, labelsize=18, bottom=False)
#     ax.tick_params(axis='x', labelsize=18, bottom=False, labelrotation=0)
#
#     ax.set_xticks(x)
#
#     ax.set_ylabel(y_label_name)  # Energy Consumption(Wh) Bitrate(Mbps) Delay(s)
#
#     max_value = max(max(row) for row in data)
#     ax.set_ylim(bottom=y_bottom, top=max_value * 1.1)
#
#     ax.set_xticklabels(labels)
#
#     linewidth = 1.5
#     for spine in ['top', 'bottom', 'left', 'right']:
#         ax.spines[spine].set_linewidth(linewidth)
#
#     bar_spacing = 1.1  # 柱子之间的间距倍数（1.0 为紧挨着，越大越松散）
#
#     # 偏移值计算方式（中心对称）
#     offsets = [-1.5, -0.5, 0.5, 1.5, 2.5, 3.5]
#     offsets = [i * bar_spacing * width for i in offsets]
#
#     # 绘制柱子
#     ax.bar(x + offsets[0], [row[0] for row in data], width, label='Vaser',
#            edgecolor='lightgoldenrodyellow', color='#B24475', linewidth=.8, hatch='x')
#
#     ax.bar(x + offsets[1], [row[1] for row in data], width, label='VAAC',
#            edgecolor='#FAEBD7', color='#864CBC', linewidth=.8, hatch='o')
#
#     ax.bar(x + offsets[2], [row[2] for row in data], width, label='VAAC-E',
#            edgecolor='#FAEBD7', color='#386688', linewidth=.8, hatch='/')
#
#     ax.bar(x + offsets[3], [row[3] for row in data], width, label='PW',
#            edgecolor='#FAEBD7', color='#845D1C', linewidth=.8, hatch='+')
#
#     ax.bar(x + offsets[4], [row[4] for row in data], width, label='BCD',
#            edgecolor='#FAEBD7', color='#8A543C', linewidth=.8, hatch='\\')
#
#     ax.bar(x + offsets[5], [row[5] for row in data], width, label='Vega',
#            edgecolor='#FAEBD7', color='#3D7747', linewidth=.8, hatch='//')
#
#     algorithms = ['Vaser', 'VAAC', 'VAAC-E', 'PW', 'BCD', 'Vega']
#
#     for i in range(len(x)):  # 遍历每个x位置（也就是每组柱子）
#         for j in range(6):  # 每组里的6个柱子
#             ax.text(
#                 x[i] + offsets[j],
#                 y_bottom - (max_value * 0.05),  # 让文字在柱子下方一点点
#                 algorithms[j],
#                 ha='center',
#                 va='top',
#                 fontsize=18,
#                 rotation=0
#             )
#
#     plt.show()
