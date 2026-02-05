import pandas as pd

# 读取CSV文件
df = pd.read_csv('./record/BCD_record.csv')

# 对每个值：乘0.01，再乘3，然后求和
# 等价于：每个值乘0.03后求和
result = (df['avg_frame_bitrate'] * 0.01 * 3.7/(8.0*1024*1024)).sum()

print(f"计算结果：{result}")