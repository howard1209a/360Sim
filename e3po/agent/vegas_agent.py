import math
import random

from e3po.agent.agent import Agent
from e3po.utils.motion_trace import predict_motion
from e3po.utils.projection_utilities import fov_to_3d_polar_coord, _3d_polar_coord_to_pixel_coord
import numpy as np
import scipy.stats as stats
from simanneal import Annealer


class VegasAgent(Agent):
    def __init__(self):
        super().__init__()
        self.m = 90  # m是x方向、横向、经度，单位是度
        self.n = 90  # n是y方向、竖向、纬度，单位是度
        self.eta = 2 # 控制l_stall和l_black在L效用中的加权比例 0.8
        self.k_lower_bound = 0
        self.k_upper_bound = max((180 - self.n) / 2.0, (360 - self.m) / 2.0)
        self.l_lower_bound = 0.5
        self.l_upper_bound = 6

        self.bandwidth_mean = None
        self.bandwidth_variance = None
        self.a_x_mean = None
        self.a_x_std = None
        self.a_y_mean = None
        self.a_y_std = None

        self.data_list = []  # 滚动更新的历史决策data列表
        self.data_list_size = 10  # 历史决策data列表长度

        self.bit2MB = 8388608.0

        self.anneal_tmax = 50.0
        self.anneal_tmin = 1e-6
        self.anneal_steps = 8000

        self.s_t_redundancy = 1.0 # 0.9

        self.v2lk_list = []
        self.v2lk_file_path = r"D:\codes\360Sim\e3po\result\dynamic_chunk\vega_v_kl.txt"

    def make_decision(self, buffer_length, motion_history, bandwidth_history, bitrate_list, tile_count, netSim):
        # lazy loading
        if self.bandwidth_mean is None or self.bandwidth_variance is None:
            self.load_bandwidth_model(netSim)
        if self.a_x_mean is None or self.a_x_std is None or self.a_y_mean is None or self.a_y_std is None:
            self.load_a_model(netSim)

        yaw, pitch = predict_motion(motion_history, netSim.motion_clock_interval, buffer_length)

        if len(self.data_list) == 0:
            self.init_data_set(netSim, yaw, pitch, bitrate_list[len(bitrate_list) - 1] * 1000, buffer_length,
                               motion_history)
        else:
            # 记录上一个chunk的真实f
            new_f = self.compute_real_f(netSim)
            self.data_list[len(self.data_list) - 1].set_f(new_f)

        init_state = [(self.l_lower_bound + self.l_upper_bound) / 2.0, 22.5]
        problem = AnnealerAgent(init_state, self, netSim, yaw, pitch, bitrate_list[len(bitrate_list) - 1] * 1000,
                                buffer_length, motion_history)
        problem.set_schedule(
            {'tmax': self.anneal_tmax, 'tmin': self.anneal_tmin, 'steps': self.anneal_steps, 'updates': 0})
        state, _ = problem.anneal()
        decision_l = state[0]
        decision_k = state[1]
        decision_L = self.compute_L(decision_k, decision_l, netSim, yaw, pitch,
                                    bitrate_list[len(bitrate_list) - 1] * 1000, buffer_length, motion_history)

        tile_point_count_list = netSim.get_point_distribution(yaw, pitch,
                                                              [self.m + 2 * decision_k, self.n + 2 * decision_k],
                                                              [50, 50])
        download_decision = [True if count > 0 else False for count in tile_point_count_list]
        bitrate_decision = [bitrate_list[len(bitrate_list) - 1]] * tile_count

        # 记录本次新增data，该data对应的真实f会在此chunk下载完后获得
        self.data_list.append(Data(decision_l, decision_k, decision_L, 0))
        # 滚动更新，删除列表中最旧的数据
        del self.data_list[0]

        # 记录一下当前速度v到k、l决策结果的映射关系
        now_pos = motion_history[len(motion_history) - 1]
        pre_pos = motion_history[len(motion_history) - 101]
        self.v2lk_list.append(
            (abs(now_pos["yaw"] - pre_pos["yaw"]), abs(now_pos["pitch"] - pre_pos["pitch"]), decision_k, decision_l))

        return download_decision, bitrate_decision, decision_l

    def record_v2lk_list(self):
        # 结束后记录chunk列表中每个chunk的数据量和下载耗时
        with open(self.v2lk_file_path, 'a') as f:
            for v2lk in self.v2lk_list:
                f.write(f"{v2lk[0]} {v2lk[1]} {v2lk[2]} {v2lk[3]}\n")

    def compute_real_f(self, netSim):
        last_chunk = netSim.chunk_list[len(netSim.chunk_list) - 1]
        start_download_clock = last_chunk.start_download_clock
        end_download_clock = last_chunk.end_download_clock

        black_ratio_list = []
        stall_count = 0

        for record in netSim.record_result_list:
            if record["clock"] >= start_download_clock and record["clock"] <= end_download_clock:
                black_ratio_list.append(record["black_ratio_in_view"])
                if record["is_rebuffer"]:
                    stall_count += 1
        stall_time = stall_count * 0.01
        avg_black_ratio = sum(black_ratio_list) / len(black_ratio_list)

        return stall_time + self.eta * avg_black_ratio

    def init_data_set(self, netSim, yaw, pitch, bitrate, buffer_length, motion_history):
        for i in range(self.data_list_size):
            sample_k = round(random.uniform(self.k_lower_bound, self.k_upper_bound), 2)
            sample_l = round(random.uniform(self.l_lower_bound, self.l_upper_bound), 2)
            L = self.compute_L(sample_k, sample_l, netSim, yaw, pitch, bitrate, buffer_length, motion_history)
            f = L
            self.data_list.append(Data(sample_l, sample_k, L, f))

    def load_bandwidth_model(self, netSim):
        # 吞吐量单位转为bit，再转为MB
        bandwidth_record = [value * 8 / self.bit2MB for value in netSim.bandwidth_record]
        data = np.array(bandwidth_record)
        # 使用正态分布拟合数据
        mean, std = stats.norm.fit(data)
        variance = std ** 2
        self.bandwidth_mean = mean
        self.bandwidth_variance = variance

    def load_a_model(self, netSim):
        # 转换所有的pitch和yaw为角度制
        angles = [
            {'pitch': self.radians_to_degrees(record[1]['pitch']), 'yaw': self.radians_to_degrees(record[1]['yaw'])} for
            record in netSim.motion_record.items()]
        angles = [angles[i] for i in range(0, len(angles), netSim.motion_clock_rate)]
        pitch_velocity = []
        yaw_velocity = []
        pitch_acceleration = []
        yaw_acceleration = []
        # 计算速度
        for i in range(1, len(angles)):
            pitch_velocity.append((angles[i]['pitch'] - angles[i - 1]['pitch']))
            yaw_velocity.append((angles[i]['yaw'] - angles[i - 1]['yaw']))
        # 计算加速度
        for i in range(1, len(pitch_velocity)):
            pitch_acceleration.append(pitch_velocity[i] - pitch_velocity[i - 1])
            yaw_acceleration.append(yaw_velocity[i] - yaw_velocity[i - 1])
        # 使用正态分布拟合数据 a_x_mean=1.6 a_x_std=24
        self.a_x_mean, self.a_x_std = stats.norm.fit(np.array(yaw_acceleration))
        self.a_y_mean, self.a_y_std = stats.norm.fit(np.array(pitch_acceleration))

    def compute_L(self, k, l, netSim, yaw, pitch, bitrate, buffer_length, motion_history):
        l_stall = self.compute_l_stall(k, l, netSim, yaw, pitch, bitrate, buffer_length)
        l_black = self.compute_l_black(k, l, motion_history, netSim)
        return l_stall + self.eta * l_black

    def compute_l_stall(self, k, l, netSim, yaw, pitch, bitrate, buffer_length):
        eov = [self.m + 2 * k, self.n + 2 * k]
        tile_point_count_list = netSim.get_point_distribution(yaw, pitch, eov, [50, 50])
        tile_transmit_count = sum(1 for x in tile_point_count_list if x > 0)
        # s_t单位为MB
        s_t = tile_transmit_count * l * bitrate / self.bit2MB
        # 留一些s_t的数据冗余防止卡顿
        s_t = s_t * self.s_t_redundancy
        b_t = buffer_length
        # 由于l_stall公式存在ln()函数，因此需要兜底判断
        if float(s_t) / b_t - self.bandwidth_mean + self.bandwidth_variance <= 0:
            pre_num = 0
        else:
            pre_num = s_t * math.exp(-1 * self.bandwidth_mean + self.bandwidth_variance / 2.0) * stats.norm.cdf(
                math.log(float(s_t) / b_t - self.bandwidth_mean + self.bandwidth_variance) / math.sqrt(
                    self.bandwidth_variance))
        if float(s_t) / b_t - self.bandwidth_mean <= 0:
            post_num = 0
        else:
            post_num = b_t * stats.norm.cdf(
                math.log(float(s_t) / b_t - self.bandwidth_mean) / math.sqrt(self.bandwidth_variance))

        l_stall = pre_num - post_num
        return l_stall

    def compute_l_black(self, k, l, motion_history, netSim):
        v_x_mean = motion_history[len(motion_history) - 1]["yaw"] - \
                   motion_history[len(motion_history) - 1 - netSim.motion_clock_rate]["yaw"]
        v_x_std = math.sqrt(self.a_x_std * l)
        v_y_mean = motion_history[len(motion_history) - 1]["pitch"] - \
                   motion_history[len(motion_history) - 1 - netSim.motion_clock_rate]["pitch"]
        v_y_std = math.sqrt(self.a_y_std * l)

        d_x_mean = v_x_mean * l
        d_x_std = math.sqrt((self.a_x_std ** 2) * (l ** 3) / 3.0)
        d_y_mean = v_y_mean * l
        d_y_std = math.sqrt((self.a_y_std ** 2) * (l ** 3) / 3.0)

        # 第一种情况，移动后FOV完全在EOV内
        x_abs = abs(d_x_mean)
        y_abs = abs(d_y_mean)
        if x_abs <= k and y_abs <= k:
            s1 = 0
            p1 = stats.norm.cdf((k - d_x_mean) / float(self.a_x_std)) * stats.norm.cdf(
                (k - d_y_mean) / float(self.a_y_std))
            black_area = s1 * p1
        elif x_abs >= k and x_abs <= self.m + k and y_abs <= k:
            s2 = self.n * (x_abs - k)
            p2 = (stats.norm.cdf((self.m + k - d_x_mean) / float(self.a_x_std)) - stats.norm.cdf(
                (k - d_x_mean) / float(self.a_x_std))) * stats.norm.cdf((k - d_y_mean) / float(self.a_y_std))
            black_area = s2 * p2
        elif x_abs <= k and y_abs >= k and y_abs <= self.n + k:
            s3 = self.m * (y_abs - k)
            p3 = stats.norm.cdf((k - d_x_mean) / float(self.a_x_std)) * (
                    stats.norm.cdf((self.n + k - d_y_mean) / float(self.a_y_std)) - stats.norm.cdf(
                (k - d_y_mean) / float(self.a_y_std)))
            black_area = s3 * p3
        elif x_abs >= k and x_abs <= self.m + k and y_abs >= k and y_abs <= self.n + k:
            s4 = self.m * self.n - (self.m + k - x_abs) * (self.n + k - y_abs)
            p4 = (stats.norm.cdf((self.m + k - d_x_mean) / float(self.a_x_std)) - stats.norm.cdf(
                (k - d_x_mean) / float(self.a_x_std))) * (
                         stats.norm.cdf((self.n + k - d_y_mean) / float(self.a_y_std)) - stats.norm.cdf(
                     (k - d_y_mean) / float(self.a_y_std)))
            black_area = s4 * p4
        else:
            s5 = self.m * self.n
            p1 = stats.norm.cdf((k - d_x_mean) / float(self.a_x_std)) * stats.norm.cdf(
                (k - d_y_mean) / float(self.a_y_std))
            p2 = (stats.norm.cdf((self.m + k - d_x_mean) / float(self.a_x_std)) - stats.norm.cdf(
                (k - d_x_mean) / float(self.a_x_std))) * stats.norm.cdf((k - d_y_mean) / float(self.a_y_std))
            p3 = stats.norm.cdf((k - d_x_mean) / float(self.a_x_std)) * (
                    stats.norm.cdf((self.n + k - d_y_mean) / float(self.a_y_std)) - stats.norm.cdf(
                (k - d_y_mean) / float(self.a_y_std)))
            p4 = (stats.norm.cdf((self.m + k - d_x_mean) / float(self.a_x_std)) - stats.norm.cdf(
                (k - d_x_mean) / float(self.a_x_std))) * (
                         stats.norm.cdf((self.n + k - d_y_mean) / float(self.a_y_std)) - stats.norm.cdf(
                     (k - d_y_mean) / float(self.a_y_std)))
            p5 = 1 - p1 - p2 - p3 - p4
            black_area = s5 * p5

        return float(black_area) / (self.m * self.n)

    def radians_to_degrees(self, radians):
        return radians * (180 / np.pi)

    # 所有瓦片均下载，所有瓦片均选择最低比特率，chunk长度为4
    def make_first_decision(self, bitrate_list, tile_count):
        dowaload_decision = [True] * tile_count
        bitrate_decision = [bitrate_list[0]] * tile_count
        chunk_length = 4
        return dowaload_decision, bitrate_decision, chunk_length

    def compute_K(self, k1, l1, k2, l2):
        l_similarity = math.exp(-1 * abs(l1 - l2) ** 2 / 2.0)
        if k1 == k2:
            k_similarity = 1
        else:
            k_similarity = abs(k1 - k2) / float(max(k1, k2))
        return l_similarity * k_similarity

    def compute_mu(self, k, l):
        K_list = []
        for data in self.data_list:
            K_list.append(self.compute_K(data.k, data.l, k, l))
        K_array = np.array(K_list)

        K_matrix = np.zeros((self.data_list_size, self.data_list_size))
        for x_index, x_data in enumerate(self.data_list):
            for y_index, y_data in enumerate(self.data_list):
                K_matrix[x_index, y_index] = self.compute_K(x_data.k, x_data.l, y_data.k, y_data.l)

        # 正则化：添加小的正则化项确保矩阵可逆
        K_matrix += np.eye(K_matrix.shape[0]) * 1e-6  # 1e-6 是一个非常小的数

        E_list = []
        for data in self.data_list:
            E_list.append(data.f - data.L)
        E_array = np.array(E_list)

        return K_array @ np.linalg.inv(K_matrix) @ E_array.T

    def compute_sigma(self, k, l):
        K_list = []
        for data in self.data_list:
            K_list.append(self.compute_K(data.k, data.l, k, l))
        K_array = np.array(K_list)

        K_matrix = np.zeros((self.data_list_size, self.data_list_size))
        for x_index, x_data in enumerate(self.data_list):
            for y_index, y_data in enumerate(self.data_list):
                K_matrix[x_index, y_index] = self.compute_K(x_data.k, x_data.l, y_data.k, y_data.l)

        # 正则化：添加小的正则化项确保矩阵可逆
        regularization = 1e-6 * np.eye(K_matrix.shape[0])
        K_matrix_regularized = K_matrix + regularization

        variance = self.compute_K(k, l, k, l) - 1 * K_array @ np.linalg.inv(K_matrix_regularized) @ K_array.T
        if variance <= 0:
            return 0
        else:
            return math.sqrt(variance)

    def compute_beta(self, netSim):
        hyper_beta = 10
        return 2 * np.log(hyper_beta * netSim.clock ** 2)


class Data():
    def __init__(self, l, k, L, f):
        self.l = l
        self.k = k
        self.L = L
        self.f = f

    def set_f(self, f):
        self.f = f


class AnnealerAgent(Annealer):
    def __init__(self, state, vegas_agent, netSim, yaw, pitch, bitrate, buffer_length, motion_history):
        super().__init__(state)
        self.vegas_agent = vegas_agent
        self.netSim = netSim
        self.yaw = yaw
        self.pitch = pitch
        self.bitrate = bitrate
        self.buffer_length = buffer_length
        self.motion_history = motion_history

    # state[0]是l，每次上下扰动l值范围/20到l值范围/5的随机浮点数，并保证不超出上下界
    # state[1]是k，每次上下扰动22.5度，并保证不超出上下界
    def move(self):
        l = self.state[0]
        l_range = self.vegas_agent.l_upper_bound - self.vegas_agent.l_lower_bound
        new_l = l + random.choice([1, -1]) * round(random.uniform(l_range / 20.0, l_range / 5.0), 2)
        if new_l > self.vegas_agent.l_upper_bound:
            new_l = self.vegas_agent.l_upper_bound
        elif new_l < self.vegas_agent.l_lower_bound:
            new_l = self.vegas_agent.l_lower_bound
        self.state[0] = new_l

        k = self.state[1]
        new_k = k + random.choice([1, -1]) * 22.5
        if new_k > self.vegas_agent.k_upper_bound or new_k < self.vegas_agent.k_lower_bound:
            new_k = k
        self.state[1] = new_k

    def energy(self):
        l = self.state[0]
        k = self.state[1]
        L = self.vegas_agent.compute_L(k, l, self.netSim, self.yaw, self.pitch, self.bitrate, self.buffer_length,
                                       self.motion_history)
        mu = self.vegas_agent.compute_mu(k, l)
        beta = self.vegas_agent.compute_beta(self.netSim)
        sigma = self.vegas_agent.compute_sigma(k, l)

        return L + mu - 1 * math.sqrt(beta) * sigma
        # return mu - 1 * math.sqrt(beta) * sigma
