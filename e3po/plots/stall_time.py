import pandas as pd
import matplotlib.pyplot as plt
from algorithm_map import csv_files, base_dir
from e3po.plots.format_draw import format_draw_histogram

rebuffer_durations = []

for algo_name, file_path in csv_files.items():
    df = pd.read_csv(base_dir + file_path)

    # 计算 clock 间隔，单位为毫秒
    if len(df['clock']) >= 2:
        interval_ms = df['clock'].iloc[1] - df['clock'].iloc[0]
    else:
        interval_ms = 0  # 或者跳过该算法

    # 卡顿帧数
    rebuffer_count = df['is_rebuffer'].sum()

    # 总卡顿时长（单位：秒）
    total_rebuffer_time = (rebuffer_count * interval_ms) / 1000.0
    rebuffer_durations.append(total_rebuffer_time)

format_draw_histogram([""], [rebuffer_durations], "", "Stall Time(s)", 0)
