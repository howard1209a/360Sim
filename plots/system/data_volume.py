import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 设置全局字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def plot_bandwidth_cdf(data_list, colors=None, markers=None, labels=None,
                       title='', show_grid=True, save_path=None,
                       num_markers=15, **kwargs):
    """
    绘制带宽数据的CDF曲线图，所有线的标记点有相同的x轴位置且等间距，标记点之间用直线连接

    参数:
    ----------
    data_list : list of lists
        带宽数据列表，每个子列表代表一条线的数据

    colors : list
        颜色列表（长度应与数据列表相同）

    markers : list
        标记形状列表

    labels : list
        图例标签列表

    title : str
        图表标题

    show_grid : bool
        是否显示网格

    save_path : str
        保存路径

    num_markers : int
        标记点数量，所有线将使用相同数量的标记点

    **kwargs :
        其他图形参数，如figure_size, line_width, alpha等
    """

    # 获取线条数量
    n_lines = len(data_list)

    # 设置默认值
    if colors is None:
        colors = [
            '#4E79A7',  # 深蓝色
            '#F28E2B',  # 橙色
            '#E15759',  # 红色
            '#76B7B2',  # 蓝绿色
            '#59A14F',  # 绿色
            '#EDC948'  # 黄色
        ]

    if markers is None:
        markers = ['o', 'v', 's', '^', 'D', 'p', '*', 'X']

    if labels is None:
        labels = [f'线路{i + 1}' for i in range(n_lines)]

    # 找到所有数据的x轴范围（最小值和最大值）
    all_values = np.concatenate(data_list)
    x_min = np.min(all_values)
    x_max = np.max(all_values)

    # 生成统一的x轴标记点位置（等间距）
    marker_x_positions = np.linspace(x_min, x_max, num_markers)

    # 创建图形
    fig_size = kwargs.get('figure_size', (12, 8))
    fig, ax = plt.subplots(figsize=fig_size)

    # 绘制每条线的CDF
    for i in range(n_lines):
        values = np.array(data_list[i])
        values_sorted = np.sort(values)

        # 计算CDF
        cdf_values = np.arange(1, len(values_sorted) + 1) / len(values_sorted)

        # 对于每个统一的x轴位置，计算对应的CDF值
        marker_cdf_values = np.zeros(num_markers)
        for j, x_pos in enumerate(marker_x_positions):
            # 找到小于等于x_pos的数据比例
            count_leq = np.sum(values_sorted <= x_pos)
            marker_cdf_values[j] = count_leq / len(values_sorted)

        # 确保第一条线从(0,0)开始，最后一条线到(最大值,1)结束
        if i == 0:  # 第一条线
            marker_cdf_values[0] = 0.0  # 确保从0开始
        if i == n_lines - 1:  # 最后一条线
            marker_cdf_values[-1] = 1.0  # 确保到1结束

        # 方法1：用折线连接这些标记点（直线连接）
        # 这里使用'-'样式，表示标记点之间用直线连接
        ax.plot(marker_x_positions, marker_cdf_values,
                linestyle='-',  # 直线连接
                color=colors[i] if i < len(colors) else None,
                linewidth=kwargs.get('line_width', 2),
                alpha=kwargs.get('alpha', 0.9),
                marker=markers[i % len(markers)],
                markersize=kwargs.get('marker_size', 8),
                markeredgecolor='white',
                markeredgewidth=1,
                label=labels[i] if i < len(labels) else f'Line {i + 1}')

        # 方法2（可选）：绘制完整的CDF曲线作为背景
        if kwargs.get('show_full_curve', False):
            ax.plot(values_sorted, cdf_values,
                    linestyle='--',
                    color=colors[i] if i < len(colors) else None,
                    linewidth=kwargs.get('line_width', 1),
                    alpha=0.3)

    # 设置图形属性
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20, fontname='SimHei')
    ax.set_xlabel('单个视频片段数据量(MB)', fontsize=12, fontname='SimHei')
    ax.set_ylabel('CDF', fontsize=12, fontname='SimHei')

    # 设置坐标轴范围
    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.05)

    # 添加网格
    if show_grid:
        ax.grid(True, alpha=0.2, linestyle='--')

    # 添加图例
    ax.legend(fontsize=11, loc='lower right',
              borderaxespad=0.5, prop={'family': 'SimHei', 'size': 10})

    # 调整布局
    plt.tight_layout()

    # 保存图片
    if save_path:
        dpi = kwargs.get('dpi', 300)
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"图片已保存至: {save_path}")

    return fig, ax


def plot_bandwidth_cdf_explicit_lines(data_list, colors=None, markers=None, labels=None,
                                      title='', show_grid=True, save_path=None,
                                      num_markers=15, **kwargs):
    """
    绘制带宽数据的CDF曲线图，明确用直线段连接相邻标记点

    这个版本更明确地展示了直线连接的过程
    """

    # 获取线条数量
    n_lines = len(data_list)

    # 设置默认值
    if colors is None:
        colors = [
            '#4E79A7',  # 深蓝色
            '#F28E2B',  # 橙色
            '#E15759',  # 红色
            '#76B7B2',  # 蓝绿色
            '#59A14F',  # 绿色
            '#EDC948'  # 黄色
        ]

    if markers is None:
        markers = ['o', 'v', 's', '^', 'D', 'p', '*', 'X']

    if labels is None:
        labels = [f'线路{i + 1}' for i in range(n_lines)]

    # 找到所有数据的x轴范围（最小值和最大值）
    all_values = np.concatenate(data_list)
    x_min = np.min(all_values)
    x_max = np.max(all_values)

    # 生成统一的x轴标记点位置（等间距）
    marker_x_positions = np.linspace(x_min, x_max, num_markers)

    # 创建图形
    fig_size = kwargs.get('figure_size', (12, 8))
    fig, ax = plt.subplots(figsize=fig_size)

    # 绘制每条线的CDF
    for i in range(n_lines):
        values = np.array(data_list[i])
        values_sorted = np.sort(values)

        # 计算CDF
        cdf_values = np.arange(1, len(values_sorted) + 1) / len(values_sorted)

        # 对于每个统一的x轴位置，计算对应的CDF值
        marker_cdf_values = np.zeros(num_markers)
        for j, x_pos in enumerate(marker_x_positions):
            # 找到小于等于x_pos的数据比例
            count_leq = np.sum(values_sorted <= x_pos)
            marker_cdf_values[j] = count_leq / len(values_sorted)

        # 确保起点和终点正确
        marker_cdf_values[0] = 0.0  # 所有线从0开始
        marker_cdf_values[-1] = 1.0  # 所有线到1结束

        # 明确用直线连接相邻标记点
        # 先绘制直线段
        for j in range(num_markers - 1):
            x_segment = [marker_x_positions[j], marker_x_positions[j + 1]]
            y_segment = [marker_cdf_values[j], marker_cdf_values[j + 1]]
            ax.plot(x_segment, y_segment,
                    linestyle='-',
                    color=colors[i] if i < len(colors) else None,
                    linewidth=kwargs.get('line_width', 2),
                    alpha=kwargs.get('alpha', 0.9))

        # 再绘制标记点
        ax.plot(marker_x_positions, marker_cdf_values,
                linestyle='',
                color=colors[i] if i < len(colors) else None,
                marker=markers[i % len(markers)],
                markersize=kwargs.get('marker_size', 8),
                markeredgecolor='white',
                markeredgewidth=1,
                label=labels[i] if i < len(labels) else f'Line {i + 1}')

    # 设置图形属性
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20, fontname='SimHei')
    ax.set_xlabel('单个视频片段数据量(MB)', fontsize=12, fontname='SimHei')
    ax.set_ylabel('CDF', fontsize=12, fontname='SimHei')

    # 设置坐标轴范围
    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.05)

    # 添加网格
    if show_grid:
        ax.grid(True, alpha=0.2, linestyle='--')

    # 添加图例
    ax.legend(fontsize=11, loc='lower right',
              borderaxespad=0.5, prop={'family': 'SimHei', 'size': 10})

    # 调整布局
    plt.tight_layout()

    # 保存图片
    if save_path:
        dpi = kwargs.get('dpi', 300)
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"图片已保存至: {save_path}")

    return fig, ax


if __name__ == "__main__":
    SPB360_live_delay_list = [
        float(x.split()[2]) / (8.0 * 1024 * 1024)
        for x in open("../raw_data/chunk_data_aggregation/SPB-360_chunk_data.csv", 'r').readlines()
    ]

    Vaser_live_delay_list = [
        float(x.split()[2]) / (8.0 * 1024 * 1024)
        for x in open("../raw_data/chunk_data_aggregation/Vaser_chunk_data.csv", 'r').readlines()
    ]

    VAAC_live_delay_list = [
        float(x.split()[2]) / (8.0 * 1024 * 1024)
        for x in open("../raw_data/chunk_data_aggregation/VAAC_chunk_data.csv", 'r').readlines()
    ]

    VAAC_E_live_delay_list = [
        float(x.split()[2]) / (8.0 * 1024 * 1024)
        for x in open("../raw_data/chunk_data_aggregation/VAAC-E_chunk_data.csv", 'r').readlines()
    ]

    PW_live_delay_list = [
        float(x.split()[2]) / (8.0 * 1024 * 1024)
        for x in open("../raw_data/chunk_data_aggregation/PW_chunk_data.csv", 'r').readlines()
    ]

    BCD_live_delay_list = [
        float(x.split()[2]) / (8.0 * 1024 * 1024)
        for x in open("../raw_data/chunk_data_aggregation/BCD_chunk_data.csv", 'r').readlines()
    ]

    all_data = [SPB360_live_delay_list, Vaser_live_delay_list, VAAC_live_delay_list, VAAC_E_live_delay_list,
                PW_live_delay_list, BCD_live_delay_list]

    custom_colors = np.vstack([plt.cm.tab10(np.linspace(0, 1, 3)), plt.cm.tab10([6, 7, 8])])

    custom_markers = ['o', 'v', 's', '^', 'D', 'p']

    custom_labels = ['SPB-360', 'Vaser', 'VAAC', 'VAAC-E', 'PW', 'BCD']

    fig1, ax1 = plot_bandwidth_cdf(
        data_list=all_data,
        colors=custom_colors,
        markers=custom_markers,
        labels=custom_labels,
        title='',
        show_grid=True,
        save_path='data_volume_uniform_markers.png',
        num_markers=45,
        figure_size=(12, 8),
        line_width=2.5,
        alpha=0.85,
        marker_size=14,
        dpi=300,
        show_full_curve=True  # 是否显示原始完整CDF曲线作为背景
    )

    plt.show()
