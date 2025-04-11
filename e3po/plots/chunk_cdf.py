from e3po.plots.format_draw import format_draw_cdf

base_dir = "/Users/howard1209a/Desktop/codes/E3PO/e3po/result/dynamic_chunk/"
agent_path_list = [base_dir + "AdaptiveBitrateAgent_chunk_data.csv", base_dir + "MotionPredictionAgent_chunk_data.csv",
                   base_dir + "MotionPredictionEOVAgent_chunk_data.csv", base_dir + "ContentEnsureAgent_chunk_data.csv",
                   base_dir + "BufferChunkAgent_chunk_data.csv", base_dir + "VegasAgent_chunk_data.csv"]

chunk_data_size_list = []
for agent_path in agent_path_list:
    data_in_mb = []
    with open(agent_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue  # 跳过空行
            parts = line.strip().split()  # 默认会把多个空格一起分割
            if len(parts) >= 1:
                bits = int(parts[0])
                mb = bits / 8.0 / 1024.0 / 1024.0  # bits → bytes → KB → MB
                data_in_mb.append(mb)

    chunk_data_size_list.append(data_in_mb)

format_draw_cdf(chunk_data_size_list[0], chunk_data_size_list[1], chunk_data_size_list[2], chunk_data_size_list[3],
                chunk_data_size_list[4], chunk_data_size_list[5], "Chunk Data/MB")
