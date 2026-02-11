import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = ["Times New Roman", "SimSun"]


def plot_bandwidth_cdf(
        labels,
        data,
        x_label_name,
        y_label_name,
        x_lim,
        y_lim,
        save_path,
        colors,
        legend_loc,
        markers,
        num_markers=25,
        line_width=1,
        font_size=10.5,
        figsize=(4, 2.5),
        legend_fontsize=8.5,
        marker_size=5,
        dpi=300
):
    n_lines = len(data)

    all_values = np.concatenate(data)
    x_min = np.min(all_values)
    x_max = np.max(all_values)

    marker_x_positions = np.linspace(x_min, x_max, num_markers)

    fig, ax = plt.subplots(figsize=figsize)

    for i in range(n_lines):
        values = np.array(data[i])
        values_sorted = np.sort(values)

        marker_cdf_values = np.zeros(num_markers)
        for j, x_pos in enumerate(marker_x_positions):
            count_leq = np.sum(values_sorted <= x_pos)
            marker_cdf_values[j] = count_leq / len(values_sorted)

        if i == 0:
            marker_cdf_values[0] = 0.0
        if i == n_lines - 1:
            marker_cdf_values[-1] = 1.0

        ax.plot(marker_x_positions, marker_cdf_values,
                linestyle='-',
                color=colors[i],
                linewidth=line_width,
                marker=markers[i],
                markersize=marker_size,
                markeredgecolor='white',
                markeredgewidth=0.3,
                label=labels[i])

    ax.set_xlabel(x_label_name, fontsize=font_size)
    ax.set_ylabel(y_label_name, fontsize=font_size)

    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)

    ax.grid(True, alpha=0.2, linestyle='--')

    ax.legend(fontsize=legend_fontsize, loc=legend_loc, frameon=False)

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    SPB360_live_delay_list = [
        float(x.split()[3]) / 1000.0
        for x in open("../raw_data/chunk_data_aggregation/SPB-360_chunk_data.csv", 'r').readlines()
    ]

    Vaser_live_delay_list = [
        float(x.split()[3]) / 1000.0
        for x in open("../raw_data/chunk_data_aggregation/Vaser_chunk_data.csv", 'r').readlines()
    ]

    VAAC_live_delay_list = [
        float(x.split()[3]) / 1000.0
        for x in open("../raw_data/chunk_data_aggregation/VAAC_chunk_data.csv", 'r').readlines()
    ]

    VAAC_E_live_delay_list = [
        float(x.split()[3]) / 1000.0
        for x in open("../raw_data/chunk_data_aggregation/VAAC-E_chunk_data.csv", 'r').readlines()
    ]

    PW_live_delay_list = [
        float(x.split()[3]) / 1000.0
        for x in open("../raw_data/chunk_data_aggregation/PW_chunk_data.csv", 'r').readlines()
    ]

    BCD_live_delay_list = [
        float(x.split()[3]) / 1000.0
        for x in open("../raw_data/chunk_data_aggregation/BCD_chunk_data.csv", 'r').readlines()
    ]

    data = [SPB360_live_delay_list, Vaser_live_delay_list, VAAC_live_delay_list, VAAC_E_live_delay_list,
            PW_live_delay_list, BCD_live_delay_list]

    colors = np.vstack([plt.cm.tab10(np.linspace(0, 1, 3)), plt.cm.tab10([6, 7, 8])])

    markers = ['o', 'v', 's', '^', 'D', 'p']

    labels = ['SPB-360', 'Vaser', 'VAAC', 'VAAC-E', 'PW', 'BCD']

    plot_bandwidth_cdf(
        labels=labels,
        data=data,
        x_label_name='单个视频片段下载时间(s)',
        y_label_name='CDF',
        x_lim=(0, 11),
        y_lim=(0, 1.05),
        save_path='download_time.png',
        colors=colors,
        legend_loc='lower right',
        markers=markers
    )
