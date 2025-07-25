import numpy as np

def read_data(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        pitch_line = lines[1].strip()
        yaw_line = lines[2].strip()
        pitch = np.array(list(map(float, pitch_line.split())))
        yaw = np.array(list(map(float, yaw_line.split())))
        return pitch, yaw

def compute_angular_speeds(pitch, yaw, interval_sec=0.01):
    assert len(pitch) == len(yaw), "pitch 和 yaw 长度不一致"
    speeds = []

    for i in range(len(pitch) - 1):
        p1 = pitch[i]
        p2 = pitch[i + 1]
        y1 = yaw[i]
        y2 = yaw[i + 1]

        # 球面夹角（球面余弦定理）
        cos_theta = np.sin(p1) * np.sin(p2) + np.cos(p1) * np.cos(p2) * np.cos(y1 - y2)
        cos_theta = np.clip(cos_theta, -1.0, 1.0)  # 防止数值误差
        d_theta = np.arccos(cos_theta)

        # 角速度 = 弧度差 / 时间间隔
        speed = d_theta / interval_sec
        speeds.append(speed)

    return speeds

def save_speeds(speeds, output_path):
    with open(output_path, 'w') as f:
        for s in speeds:
            f.write(f"{s}\n")

# 主流程
input_path = r'D:\codes\360Sim\e3po\source\motion_trace\u1_e3po.txt'        # 替换成你的真实路径
output_path = 'angular_speed_10ms.txt'

pitch, yaw = read_data(input_path)
speeds = compute_angular_speeds(pitch, yaw, interval_sec=0.01)
save_speeds(speeds, output_path)

print(f"角速度计算完成，结果共 {len(speeds)} 个，已保存至：{output_path}")
