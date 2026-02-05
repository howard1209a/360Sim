import pandas as pd

# 读取文件，指定分隔符为制表符
df = pd.read_csv("network_trace.txt", sep="\t", header=None)

# 计算前60行第二列之和（bit），转换为MB
bits_sum = df.iloc[:60, 1].sum()
mb_sum = bits_sum / (1024 * 1024*2)

print(f"前60行数据量: {mb_sum:.2f} MB")