import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = ["Times New Roman", "SimSun"]

categories = ['卡顿次数', '卡顿\n时长(s)', '画面平均质量(kbps)', '低质量\n区域\n比例']
N = len(categories)

max_values = [10, 10, 10, 10]

num_circles = 5
circle_colors = '#cecece'
circle_alpha = 1
circle_linewidth = 1

data_algo1 = [10, 10, 7, 10]  # d=1
data_algo2 = [8, 7.7, 8.2, 6.3]  # d=2
data_algo3 = [4, 3.8, 8.4, 3.5]  # d=4
data_algo4 = [2, 1.2, 10, 2.2]  # d=8

axis_labels = [
    [(0, "0"), (2, "1.2"), (4, "2.4"), (6, "3.6")],  # 上
    [(2, "8"), (4, "16"), (6, "24")],  # 右
    [(2, "1250"), (4, "2500"), (6, "3750")],  # 下
    [(2, "0.05"), (4, "0.1"), (6, "0.15")]  # 左
]

colors = np.vstack([plt.cm.tab10(np.linspace(0, 1, 3)), plt.cm.tab10([6, 7, 8])])
line_styles = ['-', '-', '-','-']
line_width = 1
fill_alpha = 0.15

axis_name_fontsize = 10.5
axis_name_fontweight = 'bold'
value_label_fontsize = 10.5
value_label_color = 'gray'

legend_fontsize = 8.5
legend_location = 'upper right'
legend_bbox_to_anchor = (1.15, 1.1)

data_algo1_closed = data_algo1 + [data_algo1[0]]
data_algo2_closed = data_algo2 + [data_algo2[0]]
data_algo3_closed = data_algo3 + [data_algo3[0]]

angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles_closed = angles + [angles[0]]


def normalize_data(data, max_vals):
    normalized = []
    for i, val in enumerate(data):
        normalized.append(val / max_vals[i] * 10)
    return normalized

norm_data_algo1 = normalize_data(data_algo1, max_values)
norm_data_algo2 = normalize_data(data_algo2, max_values)
norm_data_algo3 = normalize_data(data_algo3, max_values)
norm_data_algo4 = normalize_data(data_algo4, max_values)

norm_data_algo1_closed = norm_data_algo1 + [norm_data_algo1[0]]
norm_data_algo2_closed = norm_data_algo2 + [norm_data_algo2[0]]
norm_data_algo3_closed = norm_data_algo3 + [norm_data_algo3[0]]
norm_data_algo4_closed = norm_data_algo4 + [norm_data_algo4[0]]

fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(projection='polar'))

ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

ax.set_xticks(angles)
ax.set_xticklabels(categories, fontsize=axis_name_fontsize, fontweight=axis_name_fontweight)

ax.set_ylim(0, 10)

for i in range(num_circles):
    circle_radius = (i + 1) * 2
    ax.plot(np.linspace(0, 2 * np.pi, 100),
            [circle_radius] * 100,
            color=circle_colors,
            alpha=circle_alpha,
            linewidth=circle_linewidth,
            zorder=1)

for angle in angles:
    ax.plot([angle, angle], [0, 10],
            color='black', alpha=0.5, linewidth=1,
            zorder=2)

label_offset = 0.3

for axis_idx, angle in enumerate(angles):
    labels_on_axis = axis_labels[axis_idx]

    for radius, label_text in labels_on_axis:
        normalized_radius = radius / max_values[axis_idx] * 10

        r = normalized_radius
        theta = angle

        x = r * np.cos(theta)
        y = r * np.sin(theta)

        if axis_idx == 0:
            ha = 'left'
            va = 'center'
            x_offset = label_offset
            y_offset = 0
        elif axis_idx == 1:
            ha = 'center'
            va = 'top'
            x_offset = 0
            y_offset = -label_offset
        elif axis_idx == 2:
            ha = 'right'
            va = 'center'
            x_offset = -label_offset
            y_offset = 0
        elif axis_idx == 3:
            ha = 'center'
            va = 'bottom'
            x_offset = 0
            y_offset = label_offset
        else:
            ha = 'center'
            va = 'center'
            x_offset = 0
            y_offset = 0

        x_text = x + x_offset
        y_text = y + y_offset

        r_text = np.sqrt(x_text ** 2 + y_text ** 2)
        theta_text = np.arctan2(y_text, x_text)

        ax.text(theta_text, r_text, label_text,
                ha=ha, va=va,
                fontsize=value_label_fontsize,
                color=value_label_color,
                zorder=3)

ax.fill(angles_closed, norm_data_algo1_closed,
        alpha=fill_alpha,
        color=colors[0],
        zorder=4)

ax.fill(angles_closed, norm_data_algo2_closed,
        alpha=fill_alpha,
        color=colors[1],
        zorder=4)

ax.fill(angles_closed, norm_data_algo3_closed,
        alpha=fill_alpha,
        color=colors[2],
        zorder=4)

ax.plot(angles_closed, norm_data_algo1_closed,
        linewidth=line_width,
        label='d=1',
        color=colors[0],
        linestyle=line_styles[0],
        zorder=5)

ax.plot(angles_closed, norm_data_algo2_closed,
        linewidth=line_width,
        label='d=2',
        color=colors[1],
        linestyle=line_styles[1],
        zorder=5)

ax.plot(angles_closed, norm_data_algo3_closed,
        linewidth=line_width,
        label='d=4',
        color=colors[2],
        linestyle=line_styles[2],
        zorder=5)

ax.plot(angles_closed, norm_data_algo4_closed,
        linewidth=line_width,
        label='d=8',
        color=colors[3],
        linestyle=line_styles[3],
        zorder=5)

ax.set_yticks([])
ax.set_yticklabels([])

ax.spines['polar'].set_visible(False)

ax.grid(False)

legend = ax.legend(loc=legend_location,
                   bbox_to_anchor=legend_bbox_to_anchor,
                   fontsize=legend_fontsize,
                   frameon=True,
                   fancybox=True,
                   shadow=False)

legend.get_frame().set_facecolor('white')
legend.get_frame().set_alpha(0.9)

plt.tight_layout()
plt.savefig('window.png', dpi=300, bbox_inches='tight')
plt.show()
