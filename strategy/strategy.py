class Strategy():
    def __init__(self):
        pass

    # 根据当前时刻的缓冲区长度、头部转角历史纪录、带宽历史纪录、比特率可选等级，做出决策包括下载哪些瓦片、每个瓦片选择哪个比特率等级、chunk长度
    def make_decision(self, buffer_length, motion_history, bandwidth_history, bitrate_list, tile_list, tile_count,
                      netSim):
        pass

    # 下载第一个chunk的决策，无任何先验信息
    def make_first_decision(self, bitrate_list, tile_count):
        pass
