import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.family"] = ["Times New Roman", "SimSun"]


def plot_lines(
        data,
        x_range,
        y_left_range,
        y_right_range,
        x_label_name,
        y_left_label_name,
        y_right_label_name,
        colors,
        line_styles,
        markers,
        legend_labels,
        legend_loc,
        save_path,
        figsize=(4, 2.5),
        legend_fontsize=8.5,
        font_size=10.5,
        line_width=1,
        marker_size=3,
        dpi=300,
):
    fig, ax1 = plt.subplots(figsize=figsize)

    ax2 = ax1.twinx()

    x_time = np.arange(x_range[0], x_range[1] + 1)

    line1_data = data[0][:len(x_time)]
    line1 = ax1.plot(x_time, line1_data,
                     linestyle=line_styles[0],
                     color=colors[0],
                     marker=markers[0],
                     markersize=marker_size,
                     linewidth=line_width,
                     label=legend_labels[0])

    line2_data = data[1][:len(x_time)]
    line2 = ax2.plot(x_time, line2_data,
                     linestyle=line_styles[1],
                     color=colors[1],
                     marker=markers[1],
                     markersize=marker_size,
                     linewidth=line_width,
                     label=legend_labels[1])

    ax1.set_xlim(x_range)
    ax1.set_ylim(y_left_range)
    ax2.set_ylim(y_right_range)

    ax1.set_xlabel(x_label_name, fontsize=font_size)
    ax1.set_ylabel(y_left_label_name, fontsize=font_size)
    ax2.set_ylabel(y_right_label_name, fontsize=font_size)

    ax1.grid(True, alpha=0.2, linestyle='--', color='gray')

    lines = line1 + line2
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, fontsize=legend_fontsize, loc=legend_loc, frameon=False, ncols=2)

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    chunk_length_list = [0.5, 4.2, 3.65, 3.8, 3.95, 3.7, 3.25, 2.95, 3.89, 4.3, 3.7, 4.45, 2.05, 2.15, 4.35, 3.3, 2.87,
                         2.28, 1.35, 1.45, 6, 1.35, 0.5, 3.6, 6, 5.3, 2.3, 3, 1.9, 6, 4.7, 0.5, 0.5, 4.15, 2.8, 2.68, 6,
                         4.75, 1.85, 1.7, 0.5, 0.5, 4.08, 3.17, 3.12, 6, 4.92, 1.85, 1.81, 0.5, 0.5, 4.2, 3.3]
    velocity_list = [12, 10, 1, 0.5, 4, 4.5, 10.5, 7, 1, 23, 44, 36, 48, 33, 26.5, 2, 2.5, 1.5, 33, 26, 16, 35.5, 39.5,
                     33.5, 0.8, 0.3, 0.4, 2, 0.9, 18, 50, 8, 6.5, 6.2, 0.3, 0.4, 0.2, 10.3, 23.5, 24, 12.3, 10, 9.5, 50,
                     26, 23, 30.5, 18, 16.5, 9.5, 10.3, 10.5, 12]

    data = [chunk_length_list, velocity_list]

    colors = plt.cm.tab10(np.linspace(0, 1, 3))
    line_styles = ['-', '--']
    markers = ['o', 'x']
    legend_labels = ['视频片段长度', '水平方向角速度']

    plot_lines(
        data=data,
        x_range=(0, 52),
        y_left_range=(0, 7.5),
        y_right_range=(0, 65),
        x_label_name="时间(s)",
        y_left_label_name='视频片段长度(s)',
        y_right_label_name='水平方向角速度(°/s)',
        colors=colors,
        line_styles=line_styles,
        markers=markers,
        legend_labels=legend_labels,
        legend_loc='upper center',
        save_path='chunk_length_velocity.png',
    )
