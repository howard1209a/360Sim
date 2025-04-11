import csv
import os

import numpy as np
import random

from tqdm import tqdm

from e3po import get_opt, get_logger, read_video_json, pre_processing_client_log
from e3po.agent.adaptive_bitrate_agent import AdaptiveBitrateAgent
from e3po.agent.buffer_chunk_agent import BufferChunkAgent
from e3po.agent.content_ensure_agent import ContentEnsureAgent
from e3po.agent.lowest_bitrate_agent import LowestBitrateAgent
from e3po.agent.motion_prediction_agent import MotionPredictionAgent
from e3po.agent.motion_prediction_eov_agent import MotionPredictionEOVAgent
from e3po.agent.vegas_agent import VegasAgent
from e3po.decision.base_decision import BaseDecision
import os.path as osp
import yaml
import json

from e3po.utils.projection_utilities import fov_to_3d_polar_coord, _3d_polar_coord_to_pixel_coord
from utils.motion_trace import read_client_log

from e3po.utils.misc import generate_motion_clock


class Sim():
    def __init__(self):
        with open('config.yml', 'r', encoding='utf-8') as yaml_file:
            self.config = yaml.safe_load(yaml_file)
        self.load_motion_record()
        self.load_motion_clock()
        self.load_bandwidth_record()

    def simulation(self):
        net_sim = NetSim(self.motion_record, self.motion_clock, self.bandwidth_record, self.config)
        net_sim.start_watch()

    def load_motion_record(self):
        motion_file_path = self.config["absolute_project_path"] + "e3po/source/motion_trace/" + \
                           self.config["settings"]["motion"]["motion_file"]
        interval = int(1000 / self.config["settings"]["motion"]["motion_frequency"])
        self.motion_record = read_client_log(motion_file_path, interval, 1)

    def load_motion_clock(self):
        video_duration = self.config["settings"]["video"]["video_duration"] * 1000
        client_ts = list(self.motion_record.keys())
        max_motion_ts = video_duration if client_ts[-1] > video_duration else client_ts[-1]
        interval = int(1000 / self.config["settings"]["motion"]["motion_frequency"])
        self.motion_clock = list(range(0, max_motion_ts, interval))

    def load_bandwidth_record(self):
        network_file_path = self.config["absolute_project_path"] + "e3po/source/network_trace/" + \
                            self.config["settings"]["network"]["network_trace_file"]  # 结果文件输出路径
        # 网络吞吐量单位是字节
        self.bandwidth_record = []

        # 打开文件并读取每一行
        with open(network_file_path, 'r') as f:
            for line in f:
                columns = line.strip().split()
                self.bandwidth_record.append(float(columns[1]))


class NetSim():
    def __init__(self, motion_record, motion_clock, bandwidth_record, config):
        self.config = config  # 配置文件

        # 超参数设置
        self.motion_history_length = config["settings"]["algorithm"][
            "motion_history_length"]  # abr算法决策时所依据的历史视野角度长度，单位为ms
        self.bandwidth_history_length = config["settings"]["algorithm"][
            "bandwidth_history_length"]  # abr算法决策时所依据的历史带宽长度，单位为ms
        self.bitrate_list = config["settings"]["algorithm"]["bitrate_list"]  # 多比特率分级，从小到大，单位kbps

        # 网络模拟参数
        self.bandwidth_record = bandwidth_record  # 带宽纪录，采样率为1，单位字节
        self.motion_record = motion_record  # 视野角度纪录
        self.motion_clock_rate = config["settings"]["motion"]["motion_frequency"]  # 视野角度纪录采样率，需与视野角度纪录对应
        self.motion_clock = motion_clock  # 视频长度内的视野角度时间戳
        self.clock = 0  # 当前时刻时间戳
        self.motion_clock_interval = 1000 / self.motion_clock_rate  # 视野角度采样间隔，单位ms

        self.chunk_list = []  # 当前已下载的chunk，当一个chunk被下载下来后会加入到该列表
        self.chunk_index_playing = -1  # 当前正在播放的chunk的索引
        self.chunk_index_next = 0  # 下一个要下载的chunk索引，等于len(chunk_list)
        self.remain_chunk_data = 0  # 当前正在下载的chunk的剩余未下载数据量
        self.download_chunk_now = None  # 当前正在下载的chunk

        # 视频源参数
        self.video_width = config["settings"]["video"]["width"]  # 视频宽度
        self.video_height = config["settings"]["video"]["height"]  # 视频高度
        self.tile_count = config["settings"]["video"]["tile_width_num"] * config["settings"]["video"][
            "tile_height_num"]  # 画面tile总数
        self.video_length = config["settings"]["video"]["video_duration"]  # 视频长度，单位s

        # 播放器参数
        self.agent = None  # abr策略智能体
        self.buffer_length = 0  # 当前缓冲区长度，单位ms
        self.is_rebuffer_now = False  # 当前是否正在卡顿
        self.play_timestamp = 0  # 当前的播放时间戳
        self.range_fov = config["settings"]["motion"]["range_fov"]  # fov，单位是度，[竖向,横向]
        self.sampling_size = [50, 50]  # 视野内画面点采样率
        self.latency = 0  # 当前直播延迟
        self.isDownloadEnd = False  # 当前直播视频下载是否结束

        # 仿真结果参数
        self.record_file_path = config["absolute_project_path"] + "e3po/result/" + config[
            "group_name"] + "/" + self.config["settings"]["algorithm"]["abr_strategy"] + ".csv"  # 结果文件输出路径
        self.metric_list = ["clock", "avg_frame_bitrate", "frame_bitrate_deviation", "black_ratio_in_view",
                            "is_rebuffer",
                            "latency", "download_data_in_interval"]  # 需要纪录的指标列表
        self.record_result_list = []

        self.load_agent()

    def load_agent(self):
        abr_strategy = self.config["settings"]["algorithm"]["abr_strategy"]
        if abr_strategy == "LowestBitrateAgent":
            self.agent = LowestBitrateAgent()
        elif abr_strategy == "AdaptiveBitrateAgent":
            self.agent = AdaptiveBitrateAgent()
        elif abr_strategy == "MotionPredictionAgent":
            self.agent = MotionPredictionAgent()
        elif abr_strategy == "MotionPredictionEOVAgent":
            self.agent = MotionPredictionEOVAgent()
        elif abr_strategy == "ContentEnsureAgent":
            self.agent = ContentEnsureAgent()
        elif abr_strategy == "BufferChunkAgent":
            self.agent = BufferChunkAgent()
        elif abr_strategy == "VegasAgent":
            self.agent = VegasAgent()

    def start_watch(self):
        if os.path.exists(self.record_file_path):
            os.remove(self.record_file_path)
        with open(self.record_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(self.metric_list)

        # 决策第一个chunk，无先验信息
        dowaload_decision, bitrate_decision, chunk_length = self.agent.make_first_decision(self.bitrate_list,
                                                                                           self.tile_count)
        self.download_chunk_now = Chunk(0, dowaload_decision, bitrate_decision,
                                        chunk_length,
                                        self.play_timestamp, self.buffer_length, 0, self.config)
        self.chunk_index_next = 1
        # 单位bit
        self.remain_chunk_data = self.download_chunk_now.get_chunk_data_size()

        for clock in tqdm(self.motion_clock):
            self.clock = clock

            # 如果当前已经有正在播放的chunk，
            # 并且当前绝对时间戳减当前直播延迟（也就是当前的播放时间戳）大于当前正在播放的chunk在原视频的结束时间戳，
            # 并且当前正在播放的chunk的下一个chunk已经下载下来了，
            # 就可以切换下一个chunk播放
            if self.chunk_index_playing != -1 and self.chunk_list[
                self.chunk_index_playing].end_timestamp < self.clock - self.latency and len(
                self.chunk_list) > self.chunk_index_playing + 1:
                self.chunk_index_playing += 1

            if self.buffer_length < self.motion_clock_interval:  # 当前缓冲区会在本次间隔消耗完
                self.play_timestamp += self.buffer_length  # 播放时间戳推动buffer长度
                self.buffer_length = 0  # buffer清空
                self.is_rebuffer_now = True  # 出现卡顿
                self.latency += self.motion_clock_interval - self.buffer_length  # 积累直播延迟
            else:  # 当前缓冲区不会在本次间隔消耗完
                self.play_timestamp += self.motion_clock_interval  # 播放时间戳推动单个时间间隔
                self.buffer_length -= self.motion_clock_interval  # buffer长度缩减单个时间间隔
                self.is_rebuffer_now = False  # 未处于卡顿状态

            if self.isDownloadEnd:
                # 纪录本次时间间隔用户的播放体验
                self.record_result_single_clock(0)
                continue

            # 本次时间间隔所能消耗的带宽，单位bit
            bandwidth_in_interval = self.bandwidth_record[int(self.clock / 1000)] * 8 / self.motion_clock_rate
            if bandwidth_in_interval < self.remain_chunk_data:  # 当前正在下载chunk的剩余数据量大于本次时间间隔所能消耗的带宽，本次不能下载完一个chunk
                download_data_in_interval = bandwidth_in_interval
                self.remain_chunk_data -= bandwidth_in_interval  # 扣减当前正在下载chunk的剩余数据量
            else:  # 本次下载下来了一个chunk
                download_data_in_interval = self.remain_chunk_data
                # 如果本次下载下来的chunk为第一个chunk，则正式开始播放
                if len(self.chunk_list) == 0:
                    self.chunk_index_playing = 0

                # 记录chunk下载结束时间戳
                self.download_chunk_now.finish_download(self.clock)
                # 本次下载下来的chunk加入已下载chunk列表
                self.chunk_list.append(self.download_chunk_now)
                # 填充buffer长度
                self.buffer_length += self.download_chunk_now.chunk_length * 1000
                # 卡顿状态为未卡顿
                if self.is_rebuffer_now:
                    self.is_rebuffer_now = False
                # 立即开始下载下一个chunk，做abr决策
                dowaload_decision, bitrate_decision, chunk_length = self.agent.make_decision(self.buffer_length,
                                                                                             self.get_motion_history(),
                                                                                             self.get_bandwidth_history(),
                                                                                             self.bitrate_list,
                                                                                             self.tile_count, self)

                # 如果当前播放时间戳+buffer长度已经>=视频总长度，则下载结束接下来只需要观看
                if self.clock + self.buffer_length >= self.video_length * 1000:
                    self.isDownloadEnd = True
                else:
                    # 构建要下载的chunk
                    self.download_chunk_now = Chunk(self.chunk_index_next, dowaload_decision, bitrate_decision,
                                                    chunk_length,
                                                    self.play_timestamp, self.buffer_length, self.clock, self.config)
                    self.chunk_index_next += 1
                    # 更新当前正在下载chunk的剩余数据量为新chunk大小
                    self.remain_chunk_data = self.download_chunk_now.get_chunk_data_size()

            # 纪录本次时间间隔用户的播放体验
            self.record_result_single_clock(download_data_in_interval)

        # 结束后记录chunk列表中每个chunk的数据量和下载耗时
        with open(self.config["absolute_project_path"] + "e3po/result/" + self.config["group_name"] + "/" +
                  self.config["settings"]["algorithm"]["abr_strategy"] + "_chunk_data.csv", 'a') as f:
            for chunk in self.chunk_list:
                f.write(f"{chunk.get_chunk_data_size()} {chunk.end_download_clock - chunk.start_download_clock}\n")
        # 如果当前策略是vega，则额外记录决策v到kl映射
        if isinstance(self.agent, VegasAgent):
            self.agent.record_v2lk_list()

    def record_result_single_clock(self, download_data_in_interval):
        with open(self.record_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            avg_frame_bitrate, frame_bitrate_deviation, black_ratio_in_view = self.get_video_quality()
            writer.writerow(
                [self.clock, avg_frame_bitrate, frame_bitrate_deviation, black_ratio_in_view, self.is_rebuffer_now,
                 self.latency, download_data_in_interval])
            self.record_result_list.append({self.metric_list[0]: self.clock,
                                            self.metric_list[1]: avg_frame_bitrate,
                                            self.metric_list[2]: frame_bitrate_deviation,
                                            self.metric_list[3]: black_ratio_in_view,
                                            self.metric_list[4]: self.is_rebuffer_now,
                                            self.metric_list[5]: self.latency,
                                            self.metric_list[6]: download_data_in_interval})

    def get_video_quality(self):
        # 如果当前未下载任何chunk，则用户整个画面都是黑屏，因此质量和质量方差都是0，视野内黑边比例为1
        if len(self.chunk_list) == 0:
            return 0, 0, 0

        motion = self.motion_record[self.clock]
        tile_point_count_list = self.get_point_distribution(float(motion["yaw"]), float(motion["pitch"]),
                                                            self.range_fov, self.sampling_size)

        numbers = []
        frequencies = []
        black_point_count_in_view = 0
        for i, count in enumerate(tile_point_count_list):  # 只遍历索引和count值
            chunk = self.chunk_list[self.chunk_index_playing]
            tile = chunk.tile_list[i]
            # 没下载的话看到黑色像素点，默认比特率为0
            if not chunk.dowaload_decision[i]:
                numbers.append(0)
                black_point_count_in_view += count
            else:
                numbers.append(tile.bitrate)
            frequencies.append(count)

        total_count = sum(frequencies)
        bitrate_sum = sum([num * freq for num, freq in zip(numbers, frequencies)])
        avg_frame_bitrate = bitrate_sum / total_count
        frame_bitrate_deviation = sum(
            [((num - avg_frame_bitrate) ** 2) * freq for num, freq in zip(numbers, frequencies)]) / total_count
        black_ratio_in_view = black_point_count_in_view / total_count

        return avg_frame_bitrate, frame_bitrate_deviation, black_ratio_in_view

    def get_point_distribution(self, yaw, pitch, range_fov, sampling_size):
        # 当前视野角度+fov -> 当前全部画面采样点的uv坐标
        _3d_polar_coord = fov_to_3d_polar_coord([yaw, pitch, 0], range_fov, sampling_size)
        # 当前全部画面采样点的uv坐标 -> 当前全部画面采样点的xy坐标
        pixel_coord = _3d_polar_coord_to_pixel_coord(_3d_polar_coord, "cmp", [self.video_height, self.video_width])
        # 当前全部画面采样点的xy坐标 -> 每个瓦片内落了多少个点
        tile_point_count_list = self.pixel_coord_to_tile_point_count_list(pixel_coord)

        return tile_point_count_list

    def pixel_coord_to_tile_point_count_list(self, pixel_coord):
        chunk = self.chunk_list[self.chunk_index_playing]

        tile_point_count_list = []
        for i in range(self.tile_count):
            tile = chunk.tile_list[i]
            mask_width = (tile.start_pos_width <= pixel_coord[0]) & (
                    pixel_coord[0] < tile.start_pos_width + tile.tile_width)
            mask_height = (tile.start_pos_height <= pixel_coord[1]) & (
                    pixel_coord[1] < tile.start_pos_height + tile.tile_height)

            hit_coord_mask = mask_width & mask_height
            tile_point_count_list.append(np.sum(hit_coord_mask))

        return tile_point_count_list

    def get_motion_history(self):
        motion_history = []
        clock_index = int(max(self.clock - self.motion_history_length, 0))
        while clock_index < self.clock:
            motion_history.append(self.motion_record[clock_index])
            clock_index += self.motion_clock_interval
        return motion_history

    def get_bandwidth_history(self):
        bandwidth_history = []
        second_index = int(max((self.clock - self.bandwidth_history_length) / 1000, 0))
        while second_index < int(self.clock / 1000):
            bandwidth_history.append(self.bandwidth_record[second_index])
            second_index += 1
        return bandwidth_history


class Chunk():
    def __init__(self, chunk_index, dowaload_decision, bitrate_decision, chunk_length, play_timestamp, buffer_length,
                 start_download_clock, config):
        self.chunk_index = chunk_index  # chunk索引
        self.dowaload_decision = dowaload_decision  # 本chunk哪些瓦片被下载
        self.bitrate_decision = bitrate_decision  # 本chunk每个瓦片选择的比特率等级
        self.chunk_length = chunk_length  # 本chunk长度，单位为s
        self.start_timestamp = play_timestamp + buffer_length  # 本chunk在原视频中的开始时间戳
        self.end_timestamp = self.start_timestamp + self.chunk_length  # 本chunk在原视频中的结束时间戳
        self.start_download_clock = start_download_clock
        self.end_download_clock = None

        self.tile_width_num = config['settings']['video']["tile_width_num"]  # 横向瓦片个数
        self.tile_height_num = config['settings']['video']["tile_height_num"]  # 竖向瓦片个数
        self.tile_width = config["settings"]["video"]["width"] / self.tile_width_num  # 单个瓦片宽度
        self.tile_height = config["settings"]["video"]["height"] / self.tile_height_num  # 单个瓦片高度

        self.ffmpeg_path = config["ffmpeg_path"]  # ffmpeg路径
        self.generate_video_file_path = config["absolute_project_path"] + "e3po/source/video/" + config[
            "group_name"] + "/" + config["settings"]["video"]["video_name"].split('.')[0] + "/tile"  # 生成切片的路径
        self.video_path = config["absolute_project_path"] + "e3po/source/video/" + config["settings"]["video"][
            "video_name"]  # 原视频路径

        self.tile_list = []  # 本chunk全部tile列表

        self.generate_all_tile()

    def generate_all_tile(self):
        tile_count = self.tile_width_num * self.tile_height_num
        for i in range(tile_count):
            tile = Tile(self.chunk_index, i, self.tile_width, self.tile_height, self.tile_width_num,
                        self.generate_video_file_path)
            tile.generate(self.ffmpeg_path, self.start_timestamp, self.video_path, self.chunk_length,
                          self.bitrate_decision)
            self.tile_list.append(tile)

    def get_chunk_data_size(self):
        chunk_data_size = 0  # 单位为bit
        for i in range(len(self.tile_list)):
            if not self.dowaload_decision[i]:
                continue
            chunk_data_size += self.tile_list[i].data_size

        return chunk_data_size

    def finish_download(self, end_download_clock):
        self.end_download_clock = end_download_clock


class Tile():
    def __init__(self, chunk_index, index, tile_width, tile_height, tile_width_num, generate_video_file_path):
        self.chunk_index = chunk_index  # 本tile所属chunk索引
        self.index = index  # tile索引
        self.tile_width = tile_width  # 本tile宽度
        self.tile_height = tile_height  # 本tile高度
        self.tile_width_num = tile_width_num  # 横向瓦片个数
        self.generate_video_file_path = generate_video_file_path  # 生成切片的路径

        self.start_pos_width = self.index % self.tile_width_num * self.tile_width  # 本tile左上角横向坐标
        self.start_pos_height = self.index / self.tile_width_num * self.tile_height  # 本tile左上角竖向坐标

    def generate(self, ffmpeg_path, start_timestamp, video_path, chunk_length, bitrate_decision):
        if not os.path.exists(self.generate_video_file_path):
            os.makedirs(self.generate_video_file_path)

        tile_file_name = self.generate_video_file_path + "/chunk" + str(self.chunk_index) + "_tile" + str(
            self.index) + ".mp4"

        # 按时间轴截断、h264编码、特定比特率、按瓦片位置剪裁
        cmd = f"{ffmpeg_path} " \
              f"-ss {int(start_timestamp / 1000)} " \
              f"-i {video_path} " \
              f"-t {chunk_length} " \
              f"-preset faster " \
              f"-c:v libx264 " \
              f"-b:v {bitrate_decision[self.index]}k " \
              f"-vf crop={self.tile_width}:{self.tile_height}:{self.start_pos_width}:{self.start_pos_height} " \
              f"-y {tile_file_name} " \
              f"-loglevel error"
        os.system(cmd)

        # 直接读系统文件大小，单位bit
        self.data_size = os.path.getsize(tile_file_name) * 8
        # 得到该瓦片比特率，单位bps
        self.bitrate = self.data_size / chunk_length


def downloaded(self, clock, buffer_length):
    self.start_clock = clock + buffer_length
    self.end_clock = self.start_clock + self.chunk_length


if __name__ == '__main__':
    get_logger().info('[simulation] start')
    sim = Sim()
    sim.simulation()
    get_logger().info('[simulation] end')
