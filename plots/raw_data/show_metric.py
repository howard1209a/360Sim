import os

import pandas as pd

dict = {
    "SPB-360": "SPB-360_record.csv",
    "Vaser": "Vaser_record.csv",
    "VAAC": "VAAC_record.csv",
    "VAAC-E": "VAAC-E_record.csv",
    "PW": "PW_record.csv",
    "BCD": "BCD_record.csv"
}

stall_time_list = []

quality_list = []

low_quality_ratio_list = []

stall_count_list = []

quality_variance_list = []

for algo_name, file_path in dict.items():
    file_path = "./" + file_path
    df = pd.read_csv(file_path)

    # 卡顿帧数
    rebuffer_count = df['is_rebuffer'].sum()
    # 总卡顿时长（单位：秒）
    total_rebuffer_time = (rebuffer_count * 10) / 1000.0
    stall_time_list.append(total_rebuffer_time)

    avg_bitrate = df['avg_frame_bitrate'].mean()
    quality_list.append(avg_bitrate / 1000.0)

    avg_black = df['black_ratio_in_view'].mean()
    low_quality_ratio_list.append(avg_black)

    # 确保 is_rebuffer 是布尔值
    df['is_rebuffer'] = df['is_rebuffer'].astype(bool)
    # 找出从 False -> True 的状态跳变次数
    rebuffer_transitions = (df['is_rebuffer'].astype(int).diff() == 1).sum() + 1
    stall_count_list.append(rebuffer_transitions)

    avg_bitrate_deviation = df['frame_bitrate_deviation'].mean() / 1000000.0
    quality_variance_list.append(avg_bitrate_deviation)

print(1)
