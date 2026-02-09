import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams


def set_simple_chinese_font():
    plt.rcParams['font.sans-serif'] = ['SimSun', 'Microsoft YaHei', 'Times New Roman', 'DejaVu Sans']
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False

def format_draw_histogram(
        labels,
        data,
        x_label_name,
        y_label_name,
        y_bottom,
        y_top=None,
        bar_labels=None,
        algorithms=None,
        save_path='./info.png',
        font_family='SimHei',
        font_size=10.5,
        figsize=(4, 2.5),
        bar_width=0.18,
        group_spacing=1.2,
        colors=None,
        edge_colors=None,
        hatch_patterns=None,
        legend_fontsize=8.5,
        legend_loc='upper right',
        legend_ncol=None,  # 新增：图例列数，None表示自动
        tick_rotation=0,
        show_chinese=True
):
    """
    绘制分组柱状图

    参数:
    labels: 字符串列表，横轴标签
    data: 二维列表，形状为(len(labels), n_bars)，每个子列表包含一个横轴点对应的所有柱子高度
    x_label_name: 横轴标签名称
    y_label_name: 纵轴标签名称
    y_bottom: 纵轴最小值
    y_top: 纵轴最大值，如果为None则自动计算
    bar_labels: 柱子标签列表（图例）
    algorithms: 算法名称列表，可选，用于柱子下方标注
    save_path: 保存图片的路径
    font_family: 字体
    font_size: 字体大小
    figsize: 图形大小
    bar_width: 柱子宽度
    group_spacing: 组间间距因子
    colors: 柱子颜色列表
    edge_colors: 柱子边框颜色列表
    hatch_patterns: 填充图案列表
    legend_fontsize: 图例字体大小
    legend_loc: 图例位置
    legend_ncol: 图例列数，设置为数据条数可实现横向排列
    tick_rotation: 横轴标签旋转角度
    show_chinese: 是否显示中文
    """
    set_simple_chinese_font()

    rcParams.update({'font.size': font_size})

    fig, ax = plt.subplots(1, 1, figsize=figsize)

    # 设置坐标轴标签
    ax.set_xlabel(x_label_name, fontsize=font_size + 2)
    ax.set_ylabel(y_label_name, fontsize=font_size + 2)

    # 横坐标位置
    x = np.arange(len(labels))

    # 默认颜色方案
    default_colors = ['#B24475', '#864CBC', '#386688', '#845D1C']

    # 默认边框颜色
    default_edge_colors = ['white', 'white', 'white', 'white', 'white', 'white']

    # 默认填充图案
    default_hatch_patterns = ['x', 'o', '/', '+', '\\', '//']

    # 使用提供的参数或默认值
    if colors is None:
        colors = default_colors
    if edge_colors is None:
        edge_colors = default_edge_colors
    if hatch_patterns is None:
        hatch_patterns = default_hatch_patterns

    # 默认柱子标签
    if bar_labels is None:
        bar_labels = ['5G', 'WiFi', 'VAAC-E', 'PW', 'BCD', 'Vega']

    # 确保数据一致性
    n_bars = len(data[0]) if data else 0
    if len(bar_labels) > n_bars:
        bar_labels = bar_labels[:n_bars]
    if len(colors) > n_bars:
        colors = colors[:n_bars]
    if len(edge_colors) > n_bars:
        edge_colors = edge_colors[:n_bars]
    if len(hatch_patterns) > n_bars:
        hatch_patterns = hatch_patterns[:n_bars]

    # 计算柱子偏移 - 增加组间间距
    offsets = [((i - n_bars / 2 + 0.5) * group_spacing * bar_width) for i in range(n_bars)]

    # 设置刻度样式
    ax.tick_params(which='major', direction='in', length=5, width=1.5, labelsize=font_size)
    ax.tick_params(axis='x', labelrotation=tick_rotation)

    # 设置横轴刻度和标签
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    # 计算纵轴范围
    max_value = max(max(row) for row in data) if data else 1
    if y_top is None:
        y_top = max_value * 1.15
    ax.set_ylim(bottom=y_bottom, top=y_top)

    # 设置边框线宽
    linewidth = 1.5
    for spine in ['top', 'bottom', 'left', 'right']:
        ax.spines[spine].set_linewidth(linewidth)

    # 绘制柱子
    for idx in range(n_bars):
        bar_data = [row[idx] for row in data]
        ax.bar(x + offsets[idx], bar_data, bar_width,
               label=bar_labels[idx],
               edgecolor=edge_colors[idx],
               color=colors[idx],
               linewidth=0.9,
               hatch=hatch_patterns[idx])

    # 添加图例 - 横向排列
    if bar_labels:
        # 如果未指定列数，则使用数据条数实现横向排列
        if legend_ncol is None:
            legend_ncol = n_bars
        ax.legend(fontsize=legend_fontsize,
                  loc=legend_loc,
                  ncol=legend_ncol,  # 设置列数实现横向排列
                  frameon=True)  # 可选：是否显示图例框

    # 可选：在柱子下方添加算法名称
    if algorithms is not None:
        for i in range(len(x)):
            for j in range(min(len(algorithms), n_bars)):
                ax.text(
                    x[i] + offsets[j],
                    y_bottom - (max_value * 0.05),
                    algorithms[j],
                    ha='center',
                    va='top',
                    fontsize=font_size - 2,
                    rotation=0
                )

    # 调整布局并保存
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


# 运行测试 - 添加legend_ncol参数
if __name__ == "__main__":
    labels = ['SPB-360', 'Vaser', 'VAAC', 'VAAC-E', 'PW', 'BCD']

    data = [
        [327.53, 310.57, 136.7],
        [327.53, 324.63, 194.8],
        [327.53, 318.94, 130.1],
        [327.53, 324.58, 155.2],
        [327.53, 318.22, 100.7],
        [327.53, 326.73, 135.1],
    ]

    bar_labels = ['带宽上限', '实际传输', '有效观看']

    # 绘制图形，设置图例横向排列
    format_draw_histogram(
        labels=labels,
        data=data,
        y_label_name='数据量(MB)',
        x_label_name='',
        y_bottom=0,
        y_top=400,
        bar_labels=bar_labels,
        save_path='./data_use_horizontal_legend.png',
        font_family='SimHei',
        bar_width=0.28,
        group_spacing=1.1,
        legend_loc='upper center',  # 图例位置
        legend_ncol=3,  # 设置为数据条数实现横向排列
        # 或者使用 legend_ncol=None 自动根据数据条数设置
    )