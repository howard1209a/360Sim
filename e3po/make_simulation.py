import csv
import os

import numpy as np

from e3po import get_opt, get_logger, read_video_json, pre_processing_client_log
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

    def simulation(self):
        net_sim = NetSim(motion_clock)
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
        pass


class NetSim():
    def __init__(self, motion_record, motion_clock, config):
        self.config = config

        # 超参数设置
        self.motion_history_length = 2000
        self.bandwidth_history_length = 4000
        self.bitrate_list = [20, 50, 100]  # 从小到大，单位kbps

        # 网络模拟参数
        self.chunk_list = []
        self.chunk_index_playing = 0
        self.chunk_index_next = 0
        self.bandwidth_record = []
        self.motion_clock = motion_clock
        self.remain_chunk_data = 0
        self.clock = 0
        self.motion_clock_rate = 100  # 每秒时钟数
        self.motion_clock_interval = 10  # 单位ms，与motion_clock_rate呈倒数
        self.download_chunk_now = None
        self.motion_record = motion_record
        self.tile_list = []

        # 视频源参数
        self.video_width = config["settings"]["video"]["width"]
        self.video_height = config["settings"]["video"]["height"]
        self.tile_count = config["settings"]["video"]["tile_width_num"] * config["settings"]["video"]["tile_height_num"]

        # 播放器参数
        self.agent = None
        self.buffer_length = 0  # 单位ms
        self.is_rebuffer_now = False
        self.play_timestamp = 0
        self.range_fov = config["settings"]["motion"]["range_fov"]
        self.sampling_size = [50, 50]
        self.latency = 0

        # 仿真结果参数
        self.record_file_path = config["absolute_project_path"] + "e3po/result/" + config["group_name"] + "/result.csv"
        self.metric_list = ["clock", "avg_frame_bitrate", "frame_bitrate_deviation", "is_rebuffer", "latency"]

    def start_watch(self):
        with open(self.record_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(self.metric_list)

        for clock in self.motion_clock:
            self.clock = clock

            if self.buffer_length < 10:
                self.play_timestamp += self.buffer_length
                self.buffer_length = 0
                self.is_rebuffer_now = True
                self.latency += 10 - self.buffer_length
            else:
                self.play_timestamp += 10
                self.buffer_length -= 10
                self.is_rebuffer_now = False

            if self.clock > self.chunk_list[self.chunk_index_now].end_clock:
                self.chunk_index_now += 1
            bandwidth_interval = self.bandwidth_record[self.clock / 1000] / self.motion_clock_rate
            if bandwidth_interval < self.remain_chunk_data:
                self.remain_chunk_data -= bandwidth_interval
            else:
                self.chunk_list.append(self.download_chunk_now)
                self.buffer_length += self.download_chunk_now.chunk_length
                if self.is_rebuffer_now:
                    self.is_rebuffer_now = False
                dowaload_decision, bitrate_decision, chunk_length = self.agent.make_decision(self.buffer_length,
                                                                                             self.get_motion_history(),
                                                                                             self.get_bandwidth_history(),
                                                                                             self.bitrate_list)
                self.download_chunk_now = Chunk(self.chunk_index_next, dowaload_decision, bitrate_decision,
                                                chunk_length,
                                                self.play_timestamp, self.buffer_length, self.config)
                self.chunk_index_next += 1
                self.remain_chunk_data = self.download_chunk_now.get_chunk_data_size()

            self.record_result_single_clock()

    def record_result_single_clock(self):
        with open(self.record_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            avg_frame_bitrate, frame_bitrate_deviation = self.get_video_quality()
            writer.writerow(
                [self.clock, avg_frame_bitrate, frame_bitrate_deviation, self.is_rebuffer_now, self.latency])

    def get_video_quality(self):
        motion = self.motion_record[self.clock]
        # 当前视野角度+fov -> 当前全部画面采样点的uv坐标
        _3d_polar_coord = fov_to_3d_polar_coord([float(motion.yaw), float(motion.pitch), 0], self.range_fov,
                                                self.sampling_size)
        # 当前全部画面采样点的uv坐标 -> 当前全部画面采样点的xy坐标
        pixel_coord = _3d_polar_coord_to_pixel_coord(_3d_polar_coord, "cmp", [self.video_height, self.video_width])
        # 当前全部画面采样点的xy坐标 -> 每个瓦片内落了多少个点
        tile_point_count_list = self.pixel_coord_to_tile_point_count_list(pixel_coord)

        numbers = []
        frequencies = []
        for i, count in tile_point_count_list:
            chunk = self.chunk_list[self.chunk_index_playing]
            tile = chunk.tile_list[i]
            # 没下载的话看到黑色像素点，默认比特率为0
            if not chunk.dowaload_decision[i]:
                numbers.append(0)
            else:
                numbers.append(tile.bitrate)
            frequencies.append(count)

        total_count = sum(frequencies)
        bitrate_sum = sum([num * freq for num, freq in zip(numbers, frequencies)])
        avg_frame_bitrate = bitrate_sum / total_count
        frame_bitrate_deviation = sum(
            [((num - avg_frame_bitrate) ** 2) * freq for num, freq in zip(numbers, frequencies)]) / total_count

        return avg_frame_bitrate, frame_bitrate_deviation

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
            tile_point_count_list[i] = np.sum(hit_coord_mask)

        return tile_point_count_list

    def get_motion_history(self):
        motion_history = []
        clock_index = max(self.clock - self.motion_history_length, 0)
        while clock_index < self.clock:
            motion_history.append(self.motion_record[clock_index])
            clock_index += self.motion_clock_interval
        return motion_history

    def get_bandwidth_history(self):
        bandwidth_history = []
        second_index = max((self.clock - self.bandwidth_history_length) / 1000, 0)
        while second_index < self.clock / 1000:
            bandwidth_history.append(self.bandwidth_record[second_index])
            second_index += 1
        return bandwidth_history


class Chunk():
    def __init__(self, chunk_index, dowaload_decision, bitrate_decision, chunk_length, play_timestamp, buffer_length,
                 config):
        self.chunk_index = chunk_index
        self.dowaload_decision = dowaload_decision
        self.bitrate_decision = bitrate_decision
        self.chunk_length = chunk_length
        self.start_timestamp = play_timestamp + buffer_length
        self.end_timestamp = self.start_timestamp + self.chunk_length

        self.tile_width_num = config['settings']['video']["tile_width_num"]
        self.tile_height_num = config['settings']['video']["tile_height_num"]
        self.tile_width = config["settings"]["video"]["width"] / self.tile_width_num
        self.tile_height = config["settings"]["video"]["height"] / self.tile_height_num

        self.ffmpeg_path = config["ffmpeg_path"]
        self.generate_video_file_path = config["absolute_project_path"] + "e3po/source/video/" + config[
            "group_name"] + "/" + config["settings"]["video"]["video_name"].split('.')[0] + "/tile"
        self.video_path = config["absolute_project_path"] + "e3po/source/video/" + config["settings"]["video"][
            "video_name"]

        self.tile_list = []

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


class Tile():
    def __init__(self, chunk_index, index, tile_width, tile_height, tile_width_num, generate_video_file_path):
        self.chunk_index = chunk_index
        self.index = index
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tile_width_num = tile_width_num
        self.generate_video_file_path = generate_video_file_path

        self.start_pos_width = self.index % self.tile_width_num * self.tile_width
        self.start_pos_height = self.index / self.tile_width_num * self.tile_height

    def generate(self, ffmpeg_path, start_timestamp, video_path, chunk_length, bitrate_decision):
        if not os.path.exists(self.generate_video_file_path):
            os.makedirs(self.generate_video_file_path)

        tile_file_name = self.generate_video_file_path + "/chunk" + str(self.chunk_index) + "_tile" + str(
            self.index) + ".mp4"

        cmd = f"{ffmpeg_path} " \
              f"-ss {start_timestamp} " \
              f"-i {video_path} " \
              f"-t {chunk_length} " \
              f"-preset faster " \
              f"-c:v libx264 " \
              f"-b:v {bitrate_decision[self.index]}k " \
              f"-vf crop={self.tile_width}:{self.tile_height}:{self.start_pos_width}:{self.start_pos_height} " \
              f"-y {tile_file_name} " \
              f"-loglevel error"
        os.system(cmd)

        # 单位bit
        self.data_size = os.path.getsize(tile_file_name) * 8
        self.bitrate = self.data_size / chunk_length


def downloaded(self, clock, buffer_length):
    self.start_clock = clock + buffer_length
    self.end_clock = self.start_clock + self.chunk_length


class Agent():
    def __init__(self):
        pass

    # 当前时刻的缓冲区长度，头部转角历史纪录，带宽历史纪录，比特率可选等级
    def make_decision(self, buffer_length, motion_history, bandwidth_history, bitrate_list, tile_list):
        pass


class LowestBitrateAgent(Agent):
    def __init__(self):
        pass

    # 所有瓦片均下载，所有瓦片均选择最低比特率，chunk长度为2
    def make_decision(self, buffer_length, motion_history, bandwidth_history, bitrate_list, tile_list):
        dowaload_decision = [True] * len(tile_list)
        bitrate_decision = [0] * len(tile_list)
        chunk_length = 2
        return dowaload_decision, bitrate_decision, chunk_length


if __name__ == '__main__':
    get_logger().info('[simulation] start')
    sim = Sim()
    chunk = Chunk(0, [True] * 24, [100] * 24, 6, 0, 0,
                  sim.config)
    chunk.get_chunk_data_size()

    get_logger().info('[simulation] end')
