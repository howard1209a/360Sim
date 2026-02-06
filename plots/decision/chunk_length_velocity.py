import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 设置全局字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def plot_lines(data, x_range=(0, 59), y1_range=(0, 124000), y2_range=(0, 100),
               figure_size=(7, 5), title='', xlabel='时间(s)',
               y1_label='数据速率(kbps)', y2_label='码率选择', colors=None,
               line_styles=None, markers=None, line_width=2.5,
               show_grid=True, show_legend=True, legend_labels=None,
               legend_pos='upper right', marker_size=12, save_path=None, dpi=300):
    """
    绘制折线图（双y轴）

    参数:
    ----------
    data : list
        数据列表，包含两条线的数据

    x_range : tuple
        x轴范围 (x_min, x_max)

    y1_range : tuple
        左y轴范围 (y_min, y_max)

    y2_range : tuple
        右y轴范围 (y_min, y_max)

    figure_size : tuple
        图形尺寸

    title, xlabel : str
        标题和x轴标签

    y1_label : str
        左y轴标签

    y2_label : str
        右y轴标签

    colors : list, 可选
        颜色列表

    line_styles : list, 可选
        线条样式列表，如['-', '--']

    markers : list, 可选
        标记点样式列表，如['o', 's']

    line_width : float
        线条宽度

    show_grid : bool
        是否显示网格

    show_legend : bool
        是否显示图例

    legend_labels : list, 可选
        图例标签

    legend_pos : str
        图例位置

    marker_size : float
        标记点大小

    save_path : str, 可选
        保存路径

    dpi : int
        图片分辨率
    """

    # 设置默认值
    if colors is None:
        colors = plt.cm.tab10(np.linspace(0, 1, 2))

    if line_styles is None:
        line_styles = ['-', '--']

    if markers is None:
        markers = ['o', 's']

    if legend_labels is None:
        legend_labels = ['线路1', '线路2']

    # 创建图形和左y轴
    fig, ax1 = plt.subplots(figsize=figure_size)

    # 创建右y轴
    ax2 = ax1.twinx()

    # 生成时间轴
    x_time = np.arange(x_range[0], x_range[1] + 1)

    # 绘制第一条线（左y轴）
    line1_data = data[0][:len(x_time)]
    line1 = ax1.plot(x_time, line1_data,
                     linestyle=line_styles[0],
                     color=colors[0],
                     marker=markers[0],
                     markersize=marker_size,
                     linewidth=line_width,
                     label=legend_labels[0])

    # 绘制第二条线（右y轴）
    line2_data = data[1][:len(x_time)]
    line2 = ax2.plot(x_time, line2_data,
                     linestyle=line_styles[1],
                     color=colors[1],
                     marker=markers[1],
                     markersize=marker_size,
                     linewidth=line_width,
                     label=legend_labels[1])

    # 设置坐标轴范围
    ax1.set_xlim(x_range)
    ax1.set_ylim(y1_range)
    ax2.set_ylim(y2_range)

    # 设置标题和标签（全部黑色）
    ax1.set_title(title, fontsize=16, fontweight='bold', pad=15)
    ax1.set_xlabel(xlabel, fontsize=12, color='black')
    ax1.set_ylabel(y1_label, fontsize=12, color='black')
    ax2.set_ylabel(y2_label, fontsize=12, color='black')

    # 设置刻度颜色为黑色
    ax1.tick_params(axis='x', colors='black')
    ax1.tick_params(axis='y', colors='black')
    ax2.tick_params(axis='y', colors='black')

    # 设置x轴刻度
    start, end = x_range
    if end - start <= 60:
        tick_step = 5
    elif end - start <= 120:
        tick_step = 10
    else:
        tick_step = 20
    ax1.set_xticks(np.arange(start, end + 1, tick_step))

    # 添加网格（只为主坐标轴添加）
    if show_grid:
        ax1.grid(True, alpha=0.2, linestyle='--', color='gray')

    # 添加图例（合并两个轴的图例）
    if show_legend:
        lines = line1 + line2
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels, fontsize=11, loc=legend_pos, frameon=True)

    # 调整布局
    plt.tight_layout()

    # 保存图片
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"图片已保存至: {save_path}")

    return fig, (ax1, ax2)


if __name__ == "__main__":
    chunk_length_list = [0.5, 4.2, 3.65, 3.8, 3.95, 3.7, 3.25, 2.95, 3.89, 4.3, 3.7, 4.45, 2.05, 2.15, 4.35, 3.3, 2.87,
                         2.28, 1.35, 1.45, 6, 1.35, 0.5, 3.6, 6, 5.3, 2.3, 3, 1.9, 6, 4.7, 0.5, 0.5, 4.15, 2.8, 2.68, 6,
                         4.75, 1.85, 1.7, 0.5, 0.5, 4.08, 3.17, 3.12, 6, 4.92, 1.85, 1.81, 0.5, 0.5, 4.2, 3.3]
    velocity_list = [12, 10, 1, 0.5, 4, 4.5, 10.5, 7, 1, 23, 44, 36, 48, 33, 26.5, 2, 2.5, 1.5, 33, 26, 16, 35.5, 39.5,
                     33.5, 0.8, 0.3, 0.4, 2, 0.9, 18, 50, 8, 6.5, 6.2, 0.3, 0.4, 0.2, 10.3, 23.5, 24, 12.3, 10, 9.5, 50,
                     26, 23, 30.5, 18, 16.5, 9.5, 10.3, 10.5, 12]

    # 准备数据
    custom_data = [chunk_length_list, velocity_list]

    # 自定义设置
    custom_colors = plt.cm.tab10(np.linspace(0, 1, 3))
    custom_line_styles = ['-', '--']
    custom_markers = ['o', 'x']
    custom_legend_labels = ['视频片段长度', '水平方向角速度']

    fig, axes = plot_lines(
        data=custom_data,
        x_range=(0, 52),
        y1_range=(0, 7.5),  # 左y轴范围
        y2_range=(0, 65),  # 右y轴范围
        figure_size=(8, 5),
        title='',
        y1_label='视频片段长度(s)',  # 左y轴标签
        y2_label='水平方向角速度(°/s)',  # 右y轴标签
        colors=custom_colors,
        line_styles=custom_line_styles,
        markers=custom_markers,
        line_width=2.5,
        legend_labels=custom_legend_labels,
        legend_pos='upper right',
        marker_size=8,
        save_path='chunk_length_velocity.png'
    )

    plt.show()
