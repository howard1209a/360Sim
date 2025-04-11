import random

from e3po.agent.agent import Agent
from e3po.utils.motion_trace import predict_motion
from e3po.utils.projection_utilities import fov_to_3d_polar_coord, _3d_polar_coord_to_pixel_coord
import numpy as np


class ContentEnsureAgent(Agent):
    def __init__(self):
        super().__init__()
        self.chunk_length = 4
        self.eov = [40, 40]

    # 带宽：考虑带宽情况，采用滑动窗口预测带宽
    # 视野预测：根据历史信息预测下一秒视野落点，采用最小二乘法
    # 哪些瓦片传输：视野内一定传输，视野外如果带宽充足则传输否则不传输
    # abr策略：贪婪策略，在保证不卡顿的情况下尽可能传输高质量
    # chunk长度：固定为4

    # buffer_length单位ms
    # motion_history中的pitch纬度弧度制，yaw经度弧度制
    # bandwidth_history单位字节
    # bitrate_list单位是kbps
    def make_decision(self, buffer_length, motion_history, bandwidth_history, bitrate_list, tile_count, netSim):
        predicted_bandwidth = self.predict_bandwidth(bandwidth_history) * 8
        yaw, pitch = predict_motion(motion_history, netSim.motion_clock_interval, buffer_length)
        tile_point_count_list = netSim.get_point_distribution(yaw, pitch, self.eov, [50, 50])

        # 所有eov内的瓦片索引
        in_eov_tile = [i for i, x in enumerate(tile_point_count_list) if x > 0]
        # 所有eov外的瓦片索引
        out_eov_tile = [i for i, x in enumerate(tile_point_count_list) if x == 0]
        # 可用数据量等于buffer长度*预测带宽
        remain_data_size = int(float(buffer_length) / 1000 * predicted_bandwidth)
        # 留下一些冗余量防止卡顿
        remain_data_size = 0.7 * remain_data_size
        download_decision = [False] * tile_count
        bitrate_decision = [bitrate_list[0]] * tile_count
        # 初始所有视野内的瓦片下载低比特率，视野外不下载
        for index in in_eov_tile:
            download_decision[index] = True
            remain_data_size -= bitrate_list[0] * 1000 * self.chunk_length
        # 如果此时已经没有可用数据量，则返回
        if remain_data_size <= 0:
            return download_decision, bitrate_decision, self.chunk_length
        # 如果还有数据量，则将视野内的瓦片提升为高特率
        for index in in_eov_tile:
            bitrate_decision[index] = bitrate_list[1]
            remain_data_size -= (bitrate_list[1] - bitrate_list[0]) * 1000 * self.chunk_length
            if remain_data_size <= 0:
                return download_decision, bitrate_decision, self.chunk_length
        # 如果还有数据量，则额外下载视野外的低比特率瓦片
        for index in out_eov_tile:
            download_decision[index] = True
            bitrate_decision[index] = bitrate_list[0]
            remain_data_size -= bitrate_list[0] * 1000 * self.chunk_length
            if remain_data_size <= 0:
                return download_decision, bitrate_decision, self.chunk_length
        # 如果还有数据量，则额外下载视野外的高比特率瓦片
        for index in out_eov_tile:
            bitrate_decision[index] = bitrate_list[1]
            remain_data_size -= (bitrate_list[1] - bitrate_list[0]) * 1000 * self.chunk_length
            if remain_data_size <= 0:
                return download_decision, bitrate_decision, self.chunk_length

        return download_decision, bitrate_decision, self.chunk_length

    # 滑动窗口预测带宽
    def predict_bandwidth(self, bandwidth_history):
        return sum(bandwidth_history) / len(bandwidth_history)

    # 所有瓦片均下载，所有瓦片均选择最低比特率，chunk长度为4
    def make_first_decision(self, bitrate_list, tile_count):
        download_decision = [True] * tile_count
        bitrate_decision = [bitrate_list[0]] * tile_count
        return download_decision, bitrate_decision, self.chunk_length
