import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 设置全局字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def plot_lines(data, x_range=None, y_range=None, time_points=60,
               figure_size=(12, 5), title='', xlabel='时间(s)',
               ylabel='数据速率(kbps)', colors=None, line_styles=None,
               line_width=2, alpha=0.9, show_grid=True,
               show_legend=True, legend_labels=None, legend_pos='upper right',
               marker_mask=None, marker_size=6, save_path=None, dpi=300,
               drawstyle='default'):
    """
    绘制折线图，支持锯齿线效果

    参数:
    ----------
    data : list
        数据列表，每个元素是一条线的数据

    x_range : tuple, 可选
        x轴范围 (x_min, x_max)

    y_range : tuple, 可选
        y轴范围 (y_min, y_max)

    time_points : int
        时间点数量

    figure_size : tuple
        图形尺寸 (宽, 高)

    title : str
        图表标题

    xlabel, ylabel : str
        坐标轴标签

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
    """

    n_lines = len(data)

    # 设置默认值
    if colors is None:
        colors = plt.cm.tab10(np.linspace(0, 1, n_lines))

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
    x_time = np.arange(min(len(d) for d in data)) if data else np.arange(time_points)

    # 创建图形
    fig, ax = plt.subplots(figsize=figure_size)

    # 绘制每条线
    for i in range(n_lines):
        line_data = data[i][:len(x_time)]

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

        ax.plot(x_time, line_data,
                linestyle=line_styles[i],
                color=colors[i],
                marker=marker,
                markersize=current_marker_size,
                linewidth=line_width,
                label=legend_labels[i],
                alpha=alpha,
                markevery=markevery,
                drawstyle=drawstyles[i])  # 添加锯齿线效果

    # 设置坐标轴范围
    if x_range:
        ax.set_xlim(x_range)
    if y_range:
        ax.set_ylim(y_range)

    # 设置标题和标签
    ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)

    # 设置刻度
    ax.set_xticks(np.arange(0, len(x_time), 10))

    # 添加网格
    if show_grid:
        ax.grid(True, alpha=0.2, linestyle='--')

    # 添加图例
    if show_legend:
        ax.legend(fontsize=11, loc=legend_pos,
                  borderaxespad=0.5, frameon=True)

    # 调整布局
    plt.tight_layout()

    # 保存图片
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"图片已保存至: {save_path}")

    return fig, ax


def plot_z_lines(data, x_range=None, y_range=None, time_points=60,
                 figure_size=(12, 5), title='', xlabel='时间(s)',
                 ylabel='数据速率(kbps)', colors=None, line_styles=None,
                 line_width=2, alpha=0.9, show_grid=True,
                 show_legend=True, legend_labels=None, legend_pos='upper right',
                 marker_mask=None, marker_size=6, save_path=None, dpi=300):
    """
    简化的锯齿线绘制函数（已弃用，建议使用plot_lines的drawstyle参数）
    """
    print("警告：plot_z_lines已弃用，请使用plot_lines并设置drawstyle参数")
    return plot_lines(
        data=data,
        x_range=x_range,
        y_range=y_range,
        time_points=time_points,
        figure_size=figure_size,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        colors=colors,
        line_styles=line_styles,
        line_width=line_width,
        alpha=alpha,
        show_grid=show_grid,
        show_legend=show_legend,
        legend_labels=legend_labels,
        legend_pos=legend_pos,
        marker_mask=marker_mask,
        marker_size=marker_size,
        save_path=save_path,
        dpi=dpi,
        drawstyle='steps-post'  # 默认使用后置锯齿线
    )


# ========== 使用示例 ==========
if __name__ == "__main__":
    # 准备数据
    network_list = (pd.read_csv("../raw_data/network_trace.txt", sep="\t", header=None).iloc[:60, 1] / 2048).tolist()

    data_server2 = [99.6, 94.2, 97.4, 92.4, 98.4, 97.1, 89.2, 91.1, 84.5,
                    96.3, 79.8, 88.2, 81.8, 90.9, 96.1, 91.8, 91.1, 95.5,
                    94.0, 98.9, 97.1, 96.8, 95.6, 95.7, 97.7, 95.0, 98.4,
                    91.3, 97.3, 90.5, 96.4, 96.5, 95.3, 89.8, 93.3, 98.3,
                    96.1, 90.8, 97.1, 102, 87.8, 94.7, 92.5, 84.8, 94.9,
                    100, 98.2, 93.1, 96.3, 96.2, 96.8, 91.2, 100, 92.6,
                    93.9, 94.8, 89.8, 93.0, 96.2, 92.3]

    data_server3 = [78.0, 117.0, 110.0, 108.0, 100.0, 124.0, 109.0, 108.0,
                    87.0, 116.0, 86.0, 124.0, 8.0, 4.0, 110.0, 75.0, 13.0,
                    4.0, 116.0, 112.0, 115.0, 98.0, 13.0, 112.0, 91.0, 116.0,
                    108.0, 95.0, 125.0, 96.0, 54.0, 13.0, 106.0, 107.0,
                    121.0, 96.0, 101.0, 107.0, 110.0, 112.0, 148.0, 143.0,
                    195.0, 141.0, 14.0, 44.0, 14.0, 41.0, 30.0, 29.0, 121.0,
                    119.0, 123.0, 102.0, 106.0, 114.0, 106.0, 83.0, 112.0, 105.0]

    custom_data = [network_list, data_server2, data_server3]

    # 创建标记点掩码（仅第三条线）
    marker_mask = [i % 5 == 0 for i in range(60)]  # 每5个点显示一个标记

    # 自定义颜色和线条样式
    custom_colors = plt.cm.tab10(np.linspace(0, 1, 3))
    custom_line_styles = ['-', '-', '-']
    custom_legend_labels = ['网络带宽', '码率选择', '低质量区域比例']

    fig1, ax1 = plot_lines(
        data=custom_data,
        x_range=(0, 60),
        y_range=(0, 13000),
        figure_size=(30, 5),
        title='',
        colors=custom_colors,
        line_styles=custom_line_styles,
        line_width=2.5,
        legend_labels=custom_legend_labels,
        legend_pos='upper right',
        marker_mask=marker_mask,
        marker_size=8,
        drawstyle='steps-post',  # 所有线都使用锯齿线
        save_path='trace_SPB-360.png'
    )

    plt.show()