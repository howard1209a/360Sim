input_file = "/Users/howard1209a/Desktop/codes/E3PO/e3po/source/network_trace/5g_trace_1_driving"  # 原始文件名
output_file = "/Users/howard1209a/Desktop/codes/E3PO/e3po/source/network_trace/5g_trace_1_driving_preprocessed.txt"  # 输出文件名

with open(input_file, "r") as fin, open(output_file, "w") as fout:
    first_line = True  # 标记是否是第一行
    for line in fin:
        if not line.strip():
            continue  # 跳过空行
        time_sec, throughput_mb = map(float, line.strip().split())

        time_ms = int((time_sec - 1) * 1000)  # 其余行根据秒转换为毫秒

        throughput_bytes = int(throughput_mb * 125000)  # 吞吐量转换为字节
        fout.write(f"{time_ms}\t{throughput_bytes}\n")
