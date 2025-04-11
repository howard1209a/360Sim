import pandas as pd
import matplotlib.pyplot as plt
import os
from algorithm_map import base_dir, csv_files
from e3po.plots.format_draw import format_draw_histogram

avg_bitrate_list = []

for algo_name, file_path in csv_files.items():
    file_path = base_dir + file_path
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        avg_bitrate = df['avg_frame_bitrate'].mean()
        avg_bitrate_list.append(avg_bitrate / 8388608.0)
    else:
        print(f"文件不存在: {file_path}")

format_draw_histogram([""], [avg_bitrate_list], "", "Video Quality(MB/s)", 0)
