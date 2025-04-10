# import random
#
# from e3po.agent.agent import Agent
# from e3po.utils.projection_utilities import fov_to_3d_polar_coord, _3d_polar_coord_to_pixel_coord
#
#
# class AdaptiveBitrateAgent(Agent):
#     def __init__(self):
#         super().__init__()
#
#     # 带宽：不考虑带宽情况
#     # 视野预测：不预测，直接将最新的一个motion作为视野
#     # 哪些瓦片传输：所有瓦片都传
#     # abr策略：根据当前的用户视野结合用户fov可以计算出每个瓦片内视野采样点个数，对于全部/部分落在视野内的瓦片选择高质量，对于全部落在视野外的瓦片选择低质量
#     # chunk长度：固定为4
#     def make_decision(self, buffer_length, motion_history, bandwidth_history, bitrate_list, tile_count, netSim):
#         motion = motion_history[len(motion_history) - 1]
#         tile_point_count_list = netSim.get_point_distribution(float(motion["yaw"]), float(motion["pitch"]), [89, 89],
#                                                               [50, 50])
#         dowaload_decision = [True] * tile_count
#         bitrate_decision = [1 if count > 0 else 0 for count in tile_point_count_list]
#         chunk_length = 4
#         return dowaload_decision, bitrate_decision, chunk_length
#
#     def compute_l_stall(self, k, l, chunk_length, netSim, yaw, pitch, bitrate):
#         eov = [89 + 2 * k, 89 + 2 * k]
#         tile_point_count_list = netSim.get_point_distribution(yaw, pitch, eov, [50, 50])
#         tile_transmit_count = sum(1 for x in tile_point_count_list if x > 0)
#         st = tile_transmit_count * chunk_length * bitrate
#
#     def predict_bandwidth(self, motion_history):
#
#     # 所有瓦片均下载，所有瓦片均选择最低比特率，chunk长度为4
#     def make_first_decision(self, bitrate_list, tile_count):
#         dowaload_decision = [True] * tile_count
#         bitrate_decision = [bitrate_list[0]] * tile_count
#         chunk_length = 4
#         return dowaload_decision, bitrate_decision, chunk_length
