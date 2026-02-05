import random

from e3po.agent.agent import Agent
from e3po.utils.projection_utilities import fov_to_3d_polar_coord, _3d_polar_coord_to_pixel_coord


class AdaptiveBitrateAgent(Agent):
    def __init__(self):
        super().__init__()
        self.chunk_length = 2

    # 带宽：不考虑带宽情况
    # 视野预测：不预测，直接将最新的一个motion作为视野
    # 哪些瓦片传输：所有瓦片都传
    # abr策略：根据当前的用户视野结合用户fov可以计算出每个瓦片内视野采样点个数，对于全部/部分落在视野内的瓦片选择高质量，对于全部落在视野外的瓦片选择低质量
    # chunk长度：固定为4

    # buffer_length单位ms
    # motion_history中的pitch纬度弧度制，yaw经度弧度制
    # bandwidth_history单位字节
    # bitrate_list单位是kbps
    def make_decision(self, buffer_length, motion_history, bandwidth_history, bitrate_list, tile_count, netSim):
        motion = motion_history[len(motion_history) - 100]
        tile_point_count_list = netSim.get_point_distribution(float(motion["yaw"]), float(motion["pitch"]), [20, 20],
                                                              [50, 50])
        dowaload_decision = [True] * tile_count
        # bitrate_decision = [bitrate_list[0]] * tile_count
        bitrate_decision = [bitrate_list[1] if count > 0 else bitrate_list[0] for count in tile_point_count_list]
        return dowaload_decision, bitrate_decision, self.chunk_length

    # 所有瓦片均下载，所有瓦片均选择最低比特率，chunk长度为4
    def make_first_decision(self, bitrate_list, tile_count):
        dowaload_decision = [True] * tile_count
        bitrate_decision = [bitrate_list[0]] * tile_count
        return dowaload_decision, bitrate_decision, self.chunk_length
