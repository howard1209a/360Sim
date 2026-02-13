import pandas as pd
import numpy as np
import os

video_index = 4

for user_index in range(1, 21):
    # 读取 CSV 文件
    input_path = os.path.join(r"D:\codes\360Sim\e3po\source\motion_trace\paper\v1_video_13_vr_data_20220525T201707.csv")
    df = pd.read_csv(input_path)

    # 将 AdjustedTime 列转换为 datetime 类型
    df['AdjustedTime'] = pd.to_datetime(df['AdjustedTime'], unit='s')

    # 设置采样时间戳为索引，且索引为 DatetimeIndex
    df.set_index('AdjustedTime', inplace=True)

    # 计算每个采样点对应的视野角度
    video_width = 1920
    video_height = 1080

    angle_x_per_pixel = 360 / video_width
    angle_y_per_pixel = 180 / video_height

    # 计算视野角度
    df['Pose_Angle_x'] = df['Pose_Point_x'] * angle_x_per_pixel
    df['Pose_Angle_y'] = df['Pose_Point_y'] * angle_y_per_pixel

    # 降低采样率：每秒 100 个样本
    df_resampled = df.resample('10L').mean()  # 10 ms ≈ 每秒 100 个采样点

    # 重置索引，使其从0开始
    df_resampled.reset_index(inplace=True)
    df_resampled.index = np.arange(len(df_resampled))  # 设置索引从 0 开始

    # 输出TXT文件
    txt_output_path = os.path.join(r"D:\codes\360Sim\e3po\source\motion_trace\paper\video_9_u3.txt")

    # 提取所有行的纬度（y轴角度）和经度（x轴角度）
    latitude_degrees = df_resampled['Pose_Angle_y'].values
    longitude_degrees = df_resampled['Pose_Angle_x'].values

    # 将纬度和经度转换为弧度
    latitude_radians = np.radians(latitude_degrees)
    longitude_radians = np.radians(longitude_degrees)

    # 保存到TXT文件
    with open(txt_output_path, 'w') as f:
        f.write("\n")
        # 第一行：纬度弧度制，空格分隔
        f.write(" ".join(map(str, latitude_radians)) + "\n")
        # 第二行：经度弧度制，空格分隔
        f.write(" ".join(map(str, longitude_radians)) + "\n")
