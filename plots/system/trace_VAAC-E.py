import csv

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 设置全局字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def plot_lines(data, x_range=None, y_range=None, y2_range=(0, 1), time_points=60,
               figure_size=(12, 5), title='', xlabel='时间(s)',
               ylabel='数据速率(kbps)', y2_label='低质量区域比例', colors=None, line_styles=None,
               line_width=2, alpha=0.9, show_grid=True,
               show_legend=True, legend_labels=None, legend_pos='upper right',
               marker_mask=None, marker_size=6, save_path=None, dpi=300,
               drawstyle='default', use_dual_axis=True):
    """
    绘制折线图，支持锯齿线效果和双y轴

    参数:
    ----------
    data : list
        数据列表，每个元素是一条线的数据

    x_range : tuple, 可选
        x轴范围 (x_min, x_max)，如果为None则使用数据长度

    y_range : tuple, 可选
        左侧y轴范围 (y_min, y_max)

    y2_range : tuple, 可选
        右侧y轴范围 (y2_min, y2_max)，默认(0, 1)

    time_points : int
        时间点数量（当x_range为None时使用）

    figure_size : tuple
        图形尺寸 (宽, 高)

    title : str
        图表标题

    xlabel, ylabel : str
        左侧坐标轴标签

    y2_label : str
        右侧坐标轴标签

    colors : list, 可选
        颜色列表

    line_styles : list, 可选
        线条样式列表

    line_width : float
        线条宽度

    alpha : float
        透明度

    show_grid : bool
        是否显示网格

    show_legend : bool
        是否显示图例

    legend_labels : list, 可选
        图例标签

    legend_pos : str
        图例位置

    marker_mask : list, 可选
        标记点掩码，True表示显示标记点

    marker_size : float
        标记点大小（仅对第三条线有效）

    save_path : str, 可选
        保存路径

    dpi : int
        图片分辨率

    drawstyle : str or list
        绘制样式，可选值：'default'(平滑折线), 'steps-pre'(锯齿线前置),
        'steps-mid', 'steps-post'(锯齿线后置)。如果是列表，则为每条线指定样式

    use_dual_axis : bool
        是否使用双y轴
    """

    n_lines = len(data)

    # 设置默认值
    if colors is None:
        colors = plt.cm.tab10(np.linspace(0, 1, n_lines))
    else:
        # 确保colors是列表而不是numpy数组，用于后续判断
        colors = list(colors)

    if line_styles is None:
        line_styles = ['-'] * n_lines

    if legend_labels is None:
        legend_labels = [f'线路{i + 1}' for i in range(n_lines)]

    # 处理drawstyle参数
    if isinstance(drawstyle, str):
        drawstyles = [drawstyle] * n_lines
    else:
        drawstyles = drawstyle

    # 生成时间轴
    if x_range is not None:
        x_time = np.arange(x_range[0], x_range[1] + 1)
    else:
        x_time = np.arange(min(len(d) for d in data)) if data else np.arange(time_points)

    # 创建图形和主坐标轴
    fig, ax1 = plt.subplots(figsize=figure_size)

    # 如果需要双y轴，创建右侧坐标轴
    if use_dual_axis and n_lines >= 3:
        ax2 = ax1.twinx()
        axes = [ax1, ax1, ax2]  # 前两条线用左侧轴，第三条线用右侧轴
    else:
        ax2 = None
        axes = [ax1] * n_lines

    # 绘制每条线
    lines = []
    for i in range(n_lines):
        line_data = data[i][:len(x_time)]
        ax = axes[i] if i < len(axes) else axes[-1]

        # 确定标记点和大小
        if i == 2 and marker_mask is not None:  # 第三条线
            # 使用掩码确定标记点位置
            valid_mask = np.array(marker_mask[:len(x_time)]) if len(marker_mask) >= len(x_time) else np.ones(
                len(x_time), dtype=bool)
            marker = 'o'
            markevery = np.where(valid_mask)[0]
            current_marker_size = marker_size
        else:
            # 前两条线没有标记点
            marker = None
            markevery = None
            current_marker_size = 0

        # 绘制线条
        line, = ax.plot(x_time, line_data,
                        linestyle=line_styles[i],
                        color=colors[i],
                        marker=marker,
                        markersize=current_marker_size,
                        linewidth=line_width,
                        label=legend_labels[i],
                        alpha=alpha,
                        markevery=markevery,
                        drawstyle=drawstyles[i])
        lines.append(line)

    # 设置左侧坐标轴范围
    if x_range:
        ax1.set_xlim(x_range)
    if y_range:
        ax1.set_ylim(y_range)

    # 设置右侧坐标轴范围（如果存在）
    if ax2 is not None and y2_range:
        ax2.set_ylim(y2_range)

    # 设置标题和标签 - 所有标签颜色为黑色
    ax1.set_title(title, fontsize=16, fontweight='bold', pad=15)
    ax1.set_xlabel(xlabel, fontsize=12, color='black')
    ax1.set_ylabel(ylabel, fontsize=12, color='black')

    # 设置右侧y轴标签 - 同样为黑色
    if ax2 is not None:
        ax2.set_ylabel(y2_label, fontsize=12, color='black')

    # 设置刻度颜色为黑色
    ax1.tick_params(axis='x', colors='black')
    ax1.tick_params(axis='y', colors='black')
    if ax2 is not None:
        ax2.tick_params(axis='y', colors='black')

    # 设置x轴刻度 - 根据x_range动态调整
    if x_range:
        start, end = x_range
        if end - start <= 60:
            tick_step = 5
        elif end - start <= 120:
            tick_step = 10
        else:
            tick_step = 20
        ax1.set_xticks(np.arange(start, end + 1, tick_step))
    else:
        ax1.set_xticks(np.arange(0, len(x_time), 10))

    # 添加网格（只为主坐标轴添加）
    if show_grid:
        ax1.grid(True, alpha=0.2, linestyle='--', color='gray')

    # 合并图例
    if show_legend:
        # 如果使用双y轴，手动创建组合图例
        if ax2 is not None and n_lines >= 3:
            # 获取所有线条的句柄
            handles = lines[:2]  # 前两条线
            # 为第三条线创建独立的图例句柄（使用相同的颜色）
            line3_handle = plt.Line2D([], [], color=colors[2], linestyle=line_styles[2],
                                      linewidth=line_width, label=legend_labels[2])
            handles.append(line3_handle)
            ax1.legend(handles=handles, fontsize=11, loc=legend_pos,
                       borderaxespad=0.5, frameon=True, edgecolor='black')
        else:
            ax1.legend(fontsize=11, loc=legend_pos,
                       borderaxespad=0.5, frameon=True, edgecolor='black')

    # 调整布局
    plt.tight_layout()

    # 保存图片
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white', edgecolor='black')
        print(f"图片已保存至: {save_path}")

    return fig, (ax1, ax2) if ax2 is not None else (ax1,)


if __name__ == "__main__":
    # 网络trace
    network_list = (
            pd.read_csv("../raw_data/network_trace.txt", sep="\t", header=None).iloc[:60, 1] * 8 / 2048).tolist()

    # 比特率决策trace
    df = pd.read_csv("../raw_data/chunk_data/VAAC-E_chunk_data.csv", sep=' ', header=None,
                     names=['ms', 'value', 'col3', 'col4'])
    df['sec'] = (df['ms'] / 1000).astype(int)
    full_seconds = pd.DataFrame({'sec': range(0, 61)})
    merged = pd.merge(full_seconds, df[['sec', 'value']], on='sec', how='left')
    merged['value'] = merged['value'].ffill() / 1.3
    bitrate_list = merged['value'].tolist()

    # 低质量区域trace&卡顿trace
    black_ratio_list = []
    is_rebuffer_list = []
    with open('../raw_data/record/VAAC-E_record.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clock = int(row['clock'])
            # 筛选整数秒：0-60秒，且clock是1000的倍数
            if clock <= 60000 and clock % 1000 == 0:
                # 提取black_ratio_in_view
                black_ratio = float(row['black_ratio_in_view'])
                black_ratio_list.append(black_ratio)

                # 提取is_rebuffer并转换为布尔值
                is_rebuffer_str = row['is_rebuffer']
                is_rebuffer_bool = is_rebuffer_str.lower() == 'true'
                is_rebuffer_list.append(is_rebuffer_bool)

    custom_data = [network_list, bitrate_list, black_ratio_list]

    # 创建标记点掩码
    marker_mask = is_rebuffer_list

    # 自定义颜色和线条样式
    custom_colors = plt.cm.tab10(np.linspace(0, 1, 3))
    custom_line_styles = ['-', '-', '--']
    custom_legend_labels = ['网络带宽', '码率选择', '低质量区域比例']

    fig1, axes = plot_lines(
        data=custom_data,
        x_range=(0, 59),  # 设置x轴范围从0到60秒
        y_range=(0, 124000),  # 左侧y轴范围
        y2_range=(0, 1.3),  # 右侧y轴范围（0到1.3，对应比例）
        figure_size=(30, 5),
        title='VAAC-E',
        colors=custom_colors,
        line_styles=custom_line_styles,
        line_width=2.5,
        legend_labels=custom_legend_labels,
        legend_pos='upper right',
        marker_mask=marker_mask,
        marker_size=12,
        drawstyle='steps-post',  # 所有线都使用锯齿线
        use_dual_axis=True,  # 启用双y轴
        save_path='trace_VAAC-E.png'
    )

    plt.show()
