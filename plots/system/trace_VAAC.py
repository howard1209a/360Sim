import csv

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.family"] = ["Times New Roman", "SimSun"]


def plot_lines(
        data,
        title,
        x_range,
        y_left_range,
        y_right_range,
        x_label_name,
        y_left_label_name,
        y_right_label_name,
        colors,
        line_styles,
        legend_labels,
        legend_loc,
        marker_mask,
        save_path,
        figure_size=(5.2, 1.6),
        line_width=1,
        font_size=10.5,
        legend_fontsize=8.5,
        marker_size=3,
        dpi=300
):
    n_lines = len(data)

    x_time = np.arange(x_range[0], x_range[1] + 1)

    fig, ax1 = plt.subplots(figsize=figure_size)

    ax2 = ax1.twinx()
    axes = [ax1, ax1, ax2]

    lines = []
    for i in range(n_lines):
        line_data = data[i][:len(x_time)]
        ax = axes[i] if i < len(axes) else axes[-1]

        if i == 2 and marker_mask is not None:
            valid_mask = np.array(marker_mask[:len(x_time)]) if len(marker_mask) >= len(x_time) else np.ones(
                len(x_time), dtype=bool)
            marker = 'o'
            markevery = np.where(valid_mask)[0]
            current_marker_size = marker_size
        else:
            marker = None
            markevery = None
            current_marker_size = 0

        line, = ax.plot(x_time, line_data,
                        color=colors[i],
                        marker=marker,
                        markersize=current_marker_size,
                        linewidth=line_width,
                        label=legend_labels[i],
                        markevery=markevery,
                        drawstyle="steps-post",
                        linestyle=line_styles[i])
        lines.append(line)

    ax1.set_xlim(x_range)
    ax1.set_ylim(y_left_range)
    ax2.set_ylim(y_right_range)

    ax1.set_title(title, fontsize=font_size)

    ax1.set_xlabel(x_label_name, fontsize=font_size)
    ax1.set_ylabel(y_left_label_name, fontsize=font_size)

    ax2.set_ylabel(y_right_label_name, fontsize=font_size)

    handles = lines[:2]
    line3_handle = plt.Line2D([], [], color=colors[2], linewidth=line_width, label=legend_labels[2],
                              linestyle=line_styles[2])
    handles.append(line3_handle)
    ax1.legend(handles=handles, fontsize=legend_fontsize, ncols=3, loc=legend_loc, frameon=False)

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    # 网络trace
    network_list = (
            pd.read_csv("../raw_data/network_trace.txt", sep="\t", header=None).iloc[:60, 1] * 8 / 2048000).tolist()

    # 比特率决策trace
    df = pd.read_csv("../raw_data/chunk_data/VAAC_chunk_data.csv", sep=' ', header=None,
                     names=['ms', 'value', 'col3', 'col4'])
    df['sec'] = (df['ms'] / 1000).astype(int)
    full_seconds = pd.DataFrame({'sec': range(0, 61)})
    merged = pd.merge(full_seconds, df[['sec', 'value']], on='sec', how='left')
    merged['value'] = merged['value'].ffill() / 1300
    bitrate_list = merged['value'].tolist()

    # 低质量区域trace&卡顿trace
    black_ratio_list = []
    is_rebuffer_list = []
    with open('../raw_data/record/VAAC_record.csv', 'r') as f:
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

    data = [network_list, bitrate_list, black_ratio_list]
    marker_mask = is_rebuffer_list
    colors = plt.cm.tab10(np.linspace(0, 1, 3))
    line_styles = ['-', '-', '--']
    legend_labels = ['网络带宽', '码率选择', '低质量区域比例']

    plot_lines(
        data=data,
        title='VAAC',
        x_range=(0, 59),
        y_left_range=(0, 180),
        y_right_range=(0, 1.8),
        x_label_name="时间(s)",
        y_left_label_name="数据速率(Mbps)",
        y_right_label_name="低质量区域比例",
        colors=colors,
        line_styles=['-', '-', '--'],
        legend_labels=legend_labels,
        legend_loc="upper center",
        marker_mask=marker_mask,
        save_path="trace_VAAC.png"
    )
