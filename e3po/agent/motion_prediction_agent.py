import random

from e3po.agent.agent import Agent
from e3po.utils.motion_trace import predict_motion
from e3po.utils.projection_utilities import fov_to_3d_polar_coord, _3d_polar_coord_to_pixel_coord
import numpy as np


class MotionPredictionAgent(Agent):
    def __init__(self):
        super().__init__()
        self.chunk_length = 2
        self.eov = [59, 59]

    # 带宽：不考虑带宽情况
    # 视野预测：根据历史信息预测下一秒视野落点，采用最小二乘法
    # 哪些瓦片传输：用户预测视野内的瓦片传输，之外的不传
    # abr策略：用户预测视野内的瓦片选择高质量
    # chunk长度：固定为4

    # buffer_length单位ms
    # motion_history中的pitch纬度弧度制，yaw经度弧度制
    # bandwidth_history单位字节
    # bitrate_list单位是kbps
    def make_decision(self, buffer_length, motion_history, bandwidth_history, bitrate_list, tile_count, netSim):
        # yaw, pitch = predict_motion(motion_history, netSim.motion_clock_interval, buffer_length)
        yaw, pitch = predict_motion(motion_history, netSim.motion_clock_interval, 30000)
        tile_point_count_list = netSim.get_point_distribution(yaw, pitch, self.eov, [50, 50])
        download_decision = [True if count > 0 else False for count in tile_point_count_list]
        bitrate_decision = [bitrate_list[1]] * tile_count
        return download_decision, bitrate_decision, self.chunk_length

    # 所有瓦片均下载，所有瓦片均选择最低比特率，chunk长度为4
    def make_first_decision(self, bitrate_list, tile_count):
        download_decision = [True] * tile_count
        bitrate_decision = [bitrate_list[0]] * tile_count
        return download_decision, bitrate_decision, self.chunk_length
