import random

from e3po.agent.agent import Agent
from e3po.agent.content_ensure_agent import ContentEnsureAgent
from e3po.utils.motion_trace import predict_motion
from e3po.utils.projection_utilities import fov_to_3d_polar_coord, _3d_polar_coord_to_pixel_coord
import numpy as np


class BufferChunkAgent(ContentEnsureAgent):
    def __init__(self):
        super().__init__()

    # 带宽：不考虑带宽情况
    # 视野预测：根据历史信息预测下一秒视野落点，采用最小二乘法
    # 哪些瓦片传输：用户预测视野内的瓦片传输，之外的不传
    # abr策略：用户预测视野内的瓦片选择高质量
    # chunk长度：根据buffer长度动态决定
    def make_decision(self, buffer_length, motion_history, bandwidth_history, bitrate_list, tile_count, netSim):
        download_decision, bitrate_decision, _ = super().make_decision(buffer_length, motion_history, bandwidth_history,
                                                                       bitrate_list, tile_count, netSim)
        if buffer_length <= 2000:
            chunk_length = 4
        elif buffer_length > 2000 and buffer_length <= 4000:
            chunk_length = 6
        else:
            chunk_length = 8
        return download_decision, bitrate_decision, chunk_length

    # 所有瓦片均下载，所有瓦片均选择最低比特率，chunk长度为4
    def make_first_decision(self, bitrate_list, tile_count):
        download_decision = [True] * tile_count
        bitrate_decision = [bitrate_list[0]] * tile_count
        return download_decision, bitrate_decision, self.chunk_length
