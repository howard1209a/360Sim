import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import pandas as pd

plt.rcParams["font.family"] = ["Times New Roman", "SimSun"]


def format_draw_boxplot(
        data,
        labels,
        x_label_name,
        y_label_name,
        y_lim,
        save_path,
        colors,
        hatch_patterns,
        showfliers,
        mean_line,
        font_size=10.5,
        figsize=(4, 2.5),
        dpi=300
):
    plt.rcParams.update({'font.size': font_size})
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.set_xlabel(x_label_name, fontsize=font_size)
    ax.set_ylabel(y_label_name, fontsize=font_size)

    medianprops = {'color': 'black'}
    flierprops = {'markersize': 2}

    bp = ax.boxplot(data,
                    patch_artist=True,
                    showfliers=showfliers,
                    showmeans=False,
                    medianprops=medianprops,
                    flierprops=flierprops,
                    widths=0.6)

    for i, box in enumerate(bp['boxes']):
        box.set_facecolor(colors[i])
        box.set_hatch(hatch_patterns[i])
        box.set_edgecolor('black')

    if mean_line:
        for i, dataset in enumerate(data):
            mean_val = np.mean(dataset)
            x_pos = i + 1
            ax.hlines(mean_val, x_pos - 0.3, x_pos + 0.3, colors='red', linestyles='--', label='均值' if i == 0 else "")
            ax.scatter([x_pos - 0.3, x_pos + 0.3], [mean_val, mean_val], color='red', marker='|', s=50, zorder=5)

    ax.set_xticks(np.arange(1, len(labels) + 1))
    ax.set_xticklabels(labels, fontsize=font_size)
    y_min, y_max = y_lim
    ax.set_ylim(y_min, y_max)

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white', edgecolor='white')
    plt.show()


if __name__ == "__main__":
    SPB360_live_delay_list = [x / 1000.0 for x in
                              pd.read_csv("../raw_data/record/SPB-360_record.csv")['latency'].tolist()]
    Vaser_live_delay_list = [x / 1000.0 for x in pd.read_csv("../raw_data/record/Vaser_record.csv")['latency'].tolist()]
    VAAC_live_delay_list = [x / 1000.0 for x in pd.read_csv("../raw_data/record/VAAC_record.csv")['latency'].tolist()]
    VAAC_E_live_delay_list = [x / 1000.0 for x in
                              pd.read_csv("../raw_data/record/VAAC-E_record.csv")['latency'].tolist()]
    PW_live_delay_list = [x / 1000.0 for x in pd.read_csv("../raw_data/record/PW_record.csv")['latency'].tolist()]
    BCD_live_delay_list = [x / 1000.0 for x in pd.read_csv("../raw_data/record/BCD_record.csv")['latency'].tolist()]

    data = [
        SPB360_live_delay_list,
        Vaser_live_delay_list,
        VAAC_live_delay_list,
        VAAC_E_live_delay_list,
        PW_live_delay_list,
        BCD_live_delay_list
    ]
    labels = ['SPB-360', 'Vaser', 'VAAC', 'VAAC-E', 'PW', 'BCD']
    colors = ['#B24475', '#864CBC', '#386688', '#845D1C', '#8A543C', '#3D7747']
    hatch_patterns = ['x', 'o', '/', '+', '\\', '//']

    format_draw_boxplot(
        data=data,
        labels=labels,
        x_label_name='',
        y_label_name='直播延迟(s)',
        y_lim=(-2, 40),
        save_path='live_delay.png',
        colors=colors,
        hatch_patterns=hatch_patterns,
        showfliers=False,
        mean_line=True,
    )
