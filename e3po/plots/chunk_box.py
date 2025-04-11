from e3po.plots.format_draw import format_draw_cdf, format_draw_box

base_dir = "/Users/howard1209a/Desktop/codes/E3PO/e3po/result/dynamic_chunk/"
agent_path_list = [base_dir + "AdaptiveBitrateAgent_chunk_data.csv", base_dir + "MotionPredictionAgent_chunk_data.csv",
                   base_dir + "MotionPredictionEOVAgent_chunk_data.csv", base_dir + "ContentEnsureAgent_chunk_data.csv",
                   base_dir + "BufferChunkAgent_chunk_data.csv", base_dir + "VegasAgent_chunk_data.csv"]

chunk_download_time_list = []
for agent_path in agent_path_list:
    data_in_s = []
    with open(agent_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue  # 跳过空行
            parts = line.strip().split()  # 默认会把多个空格一起分割
            if len(parts) >= 1:
                ms = int(parts[1])
                s = ms / 1000.0  # ms → s
                data_in_s.append(s)

    chunk_download_time_list.append(data_in_s)

data = {"Vaser": chunk_download_time_list[0], "VAAC": chunk_download_time_list[1],
        "VAAC-E": chunk_download_time_list[2], "PW": chunk_download_time_list[3], "BCD": chunk_download_time_list[4],
        "Vega": chunk_download_time_list[5]}

my_pal = {"Vaser": "#B24475", "VAAC": "#864CBC", "VAAC-E": "#386688", "PW": "#845D1C", "BCD": "#8A543C",
          "Vega": "#3D7747"}

format_draw_box(data, my_pal, "Chunk Download Time/s", "pic2")
