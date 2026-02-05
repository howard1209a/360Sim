import pandas as pd

# 读取CSV文件
df = pd.read_csv('./record/SPB-360_record.csv')

# 计算下载数据总和（bit）
total_bits = df['download_data_in_interval'].sum()

# 转换为MB（1 MB = 1024 * 1024 * 8 bit）
total_mb = total_bits / (1024 * 1024 * 8)

print(f"下载数据总量：{total_bits:,.2f} bit")
print(f"换算为MB：{total_mb:.2f} MB")