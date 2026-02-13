from strategy.strategy import Strategy


class LBStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.chunk_length=4

    # 所有瓦片均下载，所有瓦片均选择最低比特率，chunk长度为4
    def make_decision(self, buffer_length, motion_history, bandwidth_history, bitrate_list, tile_count, netSim):
        dowaload_decision = [True] * tile_count
        bitrate_decision = [bitrate_list[0]] * tile_count
        return dowaload_decision, bitrate_decision, self.chunk_length

    # 所有瓦片均下载，所有瓦片均选择最低比特率，chunk长度为4
    def make_first_decision(self, bitrate_list, tile_count):
        dowaload_decision = [True] * tile_count
        bitrate_decision = [bitrate_list[0]] * tile_count
        return dowaload_decision, bitrate_decision, self.chunk_length
