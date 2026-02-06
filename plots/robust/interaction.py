import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体（如果需要）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# =================== 参数配置 ===================
# 1. 指标配置（上下左右四个方向）
categories = ['卡顿次数', '卡顿\n时长(s)', '画面平均质量(kbps)', '低质量\n区域\n比例']  # 上下左右四个指标
N = len(categories)  # 应该是4

# 2. 各指标的数值范围（可以单独设置每个指标的最大值）
# 注意：为了图形美观，建议保持类似的范围，但可以不同
max_values = [10, 10, 10, 10]  # 每个指标的最大值（用于数据归一化）

# 3. 同心圆配置
num_circles = 5  # 五个同心圆
circle_colors = '#cecece'  # 同心圆的颜色
circle_alpha = 1  # 同心圆的透明度
circle_linewidth = 2.5  # 同心圆的线宽（新增参数）

# 4. 数据配置（三个图例/算法）
data_algo1 = [10, 10, 7.3, 10]  # 高移动性 [上,右,下,左]
data_algo2 = [5, 7.2, 8.5, 8.8]  # 中移动性
data_algo3 = [5, 4, 10, 7]  #低移动性

# 5. 每个轴要标注的位置和标签
axis_labels = [
    [(0, "0"),(2, "1.2"), (4, "2.4"), (6, "3.6")], # 上
    [(2, "8"), (4, "16"), (6, "24")], # 右
    [(2, "1250"), (4, "2500"), (6, "3750")], # 下
    [(2, "0.05"), (4, "0.1"), (6, "0.15")] # 左
]

# 6. 图例颜色配置
colors = plt.cm.tab10(np.linspace(0, 1, 3))
line_styles = ['-', '-', '-']  # 线条样式
line_width = 2.5  # 线条宽度
fill_alpha = 0.15  # 降低填充透明度，避免覆盖

# 7. 字体配置
axis_name_fontsize = 28  # 轴名称字体大小
axis_name_fontweight = 'bold'  # 轴名称字体粗细
value_label_fontsize = 20  # 数值标签字体大小
value_label_color = 'gray'  # 数值标签颜色

# 8. 图例配置（新增）
legend_fontsize = 20  # 图例字体大小
legend_location = 'upper right'  # 图例位置
legend_bbox_to_anchor = (1.15, 1.0)  # 图例相对于图的偏移量（减小x值使图例更靠近）

# =================== 数据预处理 ===================
# 为了使图形闭合，需要重复第一个值
data_algo1_closed = data_algo1 + [data_algo1[0]]
data_algo2_closed = data_algo2 + [data_algo2[0]]
data_algo3_closed = data_algo3 + [data_algo3[0]]

# 计算每个角度的位置（四个指标均匀分布）
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles_closed = angles + [angles[0]]  # 闭合角度列表


# 归一化数据到统一的比例（0-1范围），然后缩放到最大半径
# 这里使用各自指标的最大值进行归一化
def normalize_data(data, max_vals):
    normalized = []
    for i, val in enumerate(data):
        normalized.append(val / max_vals[i] * 10)  # 缩放到0-10的范围
    return normalized


# 归一化数据
norm_data_algo1 = normalize_data(data_algo1, max_values)
norm_data_algo2 = normalize_data(data_algo2, max_values)
norm_data_algo3 = normalize_data(data_algo3, max_values)

norm_data_algo1_closed = norm_data_algo1 + [norm_data_algo1[0]]
norm_data_algo2_closed = norm_data_algo2 + [norm_data_algo2[0]]
norm_data_algo3_closed = norm_data_algo3 + [norm_data_algo3[0]]

# =================== 创建图形 ===================
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

# 设置角度方向（从上方开始，顺时针）
ax.set_theta_offset(np.pi / 2)  # 从上方开始（0°在顶部）
ax.set_theta_direction(-1)  # 顺时针方向

# 设置x轴标签（四个指标）- 使用配置的字体大小
ax.set_xticks(angles)
ax.set_xticklabels(categories, fontsize=axis_name_fontsize,
                   fontweight=axis_name_fontweight)

# 设置y轴范围（同心圆半径）- 使用归一化后的最大值10
ax.set_ylim(0, 10)

# =================== 绘制同心圆 ===================
# 先绘制同心圆，确保在最底层
for i in range(num_circles):
    circle_radius = (i + 1) * 2  # 2, 4, 6, 8, 10
    # 绘制圆形网格线
    ax.plot(np.linspace(0, 2 * np.pi, 100),
            [circle_radius] * 100,
            color=circle_colors,
            alpha=circle_alpha,
            linewidth=circle_linewidth,  # 使用可配置的线宽
            zorder=1)  # 设置较低的zorder确保在最底层

# =================== 绘制坐标轴 ===================
# 绘制四条主轴，确保在同心圆之上但在数据之下
for angle in angles:
    ax.plot([angle, angle], [0, 10],
            color='black', alpha=0.5, linewidth=1,
            zorder=2)  # 中等zorder

# =================== 在每个轴上标注自定义数值 ===================
# 定义标签的偏移量（相对于轴线的偏移）
label_offset = 0.3  # 稍微增加偏移量

# 遍历每个轴
for axis_idx, angle in enumerate(angles):
    # 获取该轴上的所有标注
    labels_on_axis = axis_labels[axis_idx]

    # 遍历该轴上的每个标注
    for radius, label_text in labels_on_axis:
        # 归一化半径到0-10范围（因为图形半径是10）
        normalized_radius = radius / max_values[axis_idx] * 10

        # 计算标签的位置（极坐标）
        r = normalized_radius  # 半径（归一化后的数值）
        theta = angle  # 角度（轴的位置）

        # 转换为直角坐标用于计算文本位置
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        # 根据轴的方向调整文本对齐方式
        if axis_idx == 0:  # 右侧（0°）- 卡顿次数
            ha = 'left'
            va = 'center'
            x_offset = label_offset
            y_offset = 0
        elif axis_idx == 1:  # 底部（270°）- 观看质量
            ha = 'center'
            va = 'top'
            x_offset = 0
            y_offset = -label_offset
        elif axis_idx == 2:  # 左侧（180°）- 延迟
            ha = 'right'
            va = 'center'
            x_offset = -label_offset
            y_offset = 0
        elif axis_idx == 3:  # 顶部（90°）- 抖动
            ha = 'center'
            va = 'bottom'
            x_offset = 0
            y_offset = label_offset
        else:
            ha = 'center'
            va = 'center'
            x_offset = 0
            y_offset = 0

        # 将偏移量加到直角坐标
        x_text = x + x_offset
        y_text = y + y_offset

        # 将直角坐标转换回极坐标
        r_text = np.sqrt(x_text ** 2 + y_text ** 2)
        theta_text = np.arctan2(y_text, x_text)

        # 添加文本标签，确保在同心圆之上
        ax.text(theta_text, r_text, label_text,
                ha=ha, va=va,
                fontsize=value_label_fontsize,
                color=value_label_color,
                zorder=3)  # 设置较高的zorder确保可见

# =================== 绘制数据线 ===================
# 先绘制填充区域（半透明，在最底层）
ax.fill(angles_closed, norm_data_algo1_closed,
        alpha=fill_alpha,
        color=colors[0],
        zorder=4)  # 填充区域在同心圆之上，但在线条之下

ax.fill(angles_closed, norm_data_algo2_closed,
        alpha=fill_alpha,
        color=colors[1],
        zorder=4)

ax.fill(angles_closed, norm_data_algo3_closed,
        alpha=fill_alpha,
        color=colors[2],
        zorder=4)

# 然后绘制线条（在最上层，确保清晰可见）
# 算法1
ax.plot(angles_closed, norm_data_algo1_closed,
        linewidth=line_width,
        label='高移动性',
        color=colors[0],
        linestyle=line_styles[0],
        zorder=5)  # 最高的zorder，确保线条在最上面

# 算法2
ax.plot(angles_closed, norm_data_algo2_closed,
        linewidth=line_width,
        label='中移动性',
        color=colors[1],
        linestyle=line_styles[1],
        zorder=5)

# 算法3
ax.plot(angles_closed, norm_data_algo3_closed,
        linewidth=line_width,
        label='低移动性',
        color=colors[2],
        linestyle=line_styles[2],
        zorder=5)

# =================== 隐藏不必要的元素 ===================
# 隐藏y轴刻度和标签
ax.set_yticks([])
ax.set_yticklabels([])

# 隐藏圆形边框
ax.spines['polar'].set_visible(False)

# 隐藏径向网格线
ax.grid(False)

# =================== 添加图例 ===================
# 添加图例（放在右上角，更靠近图形）
legend = ax.legend(loc=legend_location,
                   bbox_to_anchor=legend_bbox_to_anchor,  # 调整偏移量使图例更近
                   fontsize=legend_fontsize,  # 可设置的图例字体大小
                   frameon=True,
                   fancybox=True,
                   shadow=False)

# 设置图例背景颜色
legend.get_frame().set_facecolor('white')
legend.get_frame().set_alpha(0.9)

# 调整布局
plt.tight_layout()

# 显示图形
plt.show()

fig.savefig('interaction.png', dpi=300, bbox_inches='tight')