import pandas as pd
import matplotlib.pyplot as plt
import os
from algorithm_map import csv_files, base_dir
from e3po.plots.format_draw import format_draw_histogram

avg_black_ratios = []

for algo_name, file_path in csv_files.items():
    file_path = base_dir + file_path
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        avg_black = df['black_ratio_in_view'].mean()
        avg_black_ratios.append(avg_black)
    else:
        print(f"文件不存在：{file_path}")

format_draw_histogram([""], [avg_black_ratios], "", "Black Area Ratio", 0)
